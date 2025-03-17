from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import os

from pydantic import BaseModel
import redis
from datetime import datetime
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

app = FastAPI()
redis_client = redis.Redis(host='localhost', port=6379, db=0)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

security = HTTPBasic()

def get_current_admin(credentials: HTTPBasicCredentials = Depends(security)):
    auth_enabled = os.getenv("AUTH_ENABLED", "false").lower() == "true"
    if not auth_enabled:
        return "admin"  # Skip authentication if AUTH_ENABLED is False

    correct_username = "admin"
    correct_password = "admin123"
    is_correct_username = secrets.compare_digest(credentials.username, correct_username)
    is_correct_password = secrets.compare_digest(credentials.password, correct_password)

    if not (is_correct_username and is_correct_password):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return credentials.username


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/admin")
async def admin_panel(request: Request):
# async def admin_panel(request: Request, admin: str = Depends(get_current_admin)):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/tv")
async def tv_display(request: Request):
    return templates.TemplateResponse("tv.html", {"request": request})

# Rate limiting middleware
# @app.middleware("http")
# async def rate_limit(request: Request, call_next):
#     client_ip = request.client.host
#     requests = redis_client.incr(f"ip:{client_ip}")
#     if requests > 100:  # Max 100 requests per minute
#         raise HTTPException(status_code=429, detail="Too many requests")
#     response = await call_next(request)
#     return response


class TicketRequest(BaseModel):
    service_type: str

class Ticket(BaseModel):
    ticket_number: str
    service_type: str
    timestamp: str
    status: str = "waiting"

@app.post("/ticket")
async def create_ticket(ticket_request: TicketRequest):
    ticket_number = str(redis_client.incr("ticket_counter"))

    # Convert datetime to string
    timestamp_str = datetime.now().isoformat()

    ticket = Ticket(
        ticket_number=ticket_number,
        service_type=ticket_request.service_type,
        timestamp=timestamp_str  # Use string timestamp
    )

    # Store in Redis
    ticket_data = ticket.dict()
    redis_client.hset(f"ticket:{ticket_number}", mapping=ticket_data)
    redis_client.rpush("queue", ticket_number)

    return ticket

@app.get("/current")
async def get_current_ticket():
    current = redis_client.get("current_ticket")
    if not current:
        return {"current_ticket": None}
    return {"current_ticket": current}

@app.post("/next")
async def call_next_ticket():
    next_ticket = redis_client.lpop("queue")
    if next_ticket:
        redis_client.set("current_ticket", next_ticket)
        return {"next_ticket": next_ticket}
    return {"message": "No tickets in queue"}

# Error handling
@app.exception_handler(HTTPException)
async def custom_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.get("/admin/tickets")
async def get_all_tickets(admin: str = Depends(get_current_admin)):
    tickets = []
    # Get all ticket keys
    ticket_keys = redis_client.keys("ticket:*")

    for key in ticket_keys:
        # Get ticket data using HGETALL
        ticket_data = redis_client.hgetall(key)
        if ticket_data:
            # Decode keys and values from bytes to strings
            decoded_ticket = {k.decode('utf-8'): v.decode('utf-8') for k, v in ticket_data.items()}
            tickets.append(decoded_ticket)

    return sorted(tickets, key=lambda x: x['ticket_number'])

@app.post("/admin/serve/{ticket_number}")
async def serve_ticket(ticket_number: str, admin: str = Depends(get_current_admin)):
    # Check if ticket exists
    ticket_key = f"ticket:{ticket_number}"
    if not redis_client.exists(ticket_key):
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Update ticket status
    redis_client.hset(ticket_key, "status", "serving")
    # Set as current ticket
    redis_client.set("current_ticket", ticket_number)

    return {"message": f"Now serving ticket {ticket_number}"}

@app.post("/admin/complete/{ticket_number}")
async def complete_ticket(ticket_number: str, admin: str = Depends(get_current_admin)):
    ticket_key = f"ticket:{ticket_number}"
    if not redis_client.exists(ticket_key):
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Update ticket status
    redis_client.hset(ticket_key, "status", "completed")
    # Clear current ticket if it's this one
    current = redis_client.get("current_ticket")
    if current == ticket_number:
        redis_client.delete("current_ticket")

    return {"message": f"Ticket {ticket_number} completed"}

