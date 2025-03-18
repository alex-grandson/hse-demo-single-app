# Развертывание приложения очереди на K3d

Этот документ объясняет, как настроить кластер K3d и развернуть приложение очереди.

## Предварительные требования

- Установленный Docker.
- Установленный K3d. Инструкции по установке доступны [здесь](https://k3d.io/).

## Шаг 1: Создание кластера K3d

1. Создайте кластер K3d с именем `queue-cluster`:
   ```bash
   k3d cluster create queue-cluster --servers 1 --agents 2 --port "8000:30000@loadbalancer"
   ```

2. Убедитесь, что кластер работает:
   ```bash
   kubectl get nodes
   ```

## Шаг 2: Сборка и загрузка Docker-образов

1. Соберите Docker-образ для FastAPI приложения:
   ```bash
   docker build -t queue-api:latest .
   ```

2. Загрузите образ в кластер K3d:
   ```bash
   k3d image import queue-api:latest -c queue-cluster
   ```

## Шаг 3: Развертывание приложения

1. Примените манифесты Kubernetes:
   ```bash
   kubectl apply -f .k8s/
   ```

2. Проверьте развертывание:
   ```bash
   kubectl get pods
   ```

3. Проверьте сервисы:
   ```bash
   kubectl get services
   ```

## Шаг 4: Доступ к приложению

1. Найдите NodePort для сервиса `queue-api`:
   ```bash
   kubectl get service queue-api
   ```

2. Откройте приложение в браузере, используя `http://localhost:8000`.

## Очистка

Чтобы удалить кластер K3d, выполните:
```bash
k3d cluster delete queue-cluster
```
