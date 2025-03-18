# Развертывание приложения очереди на K3s

Этот документ объясняет, как настроить однопользовательский кластер K3s и развернуть приложение очереди.

## Предварительные требования

- Linux-машина с минимум 2 ГБ оперативной памяти.
- Установленный Docker.

## Шаг 1: Установка K3s

1. Выполните следующую команду для установки K3s:
   ```bash
   curl -sfL https://get.k3s.io | sh -
   ```

2. Убедитесь, что K3s работает:
   ```bash
   sudo kubectl get nodes
   ```

## Шаг 2: Сборка и загрузка Docker-образов

1. Соберите Docker-образ для FastAPI приложения:
   ```bash
   docker build -t queue-api:latest .
   ```

2. Сохраните образ в файл tar:
   ```bash
   docker save queue-api:latest -o queue-api.tar
   ```

3. Загрузите образ в кластер K3s:
   ```bash
   sudo k3s ctr images import queue-api.tar
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

2. Откройте приложение в браузере, используя `http://<node-ip>:<node-port>`.

## Очистка

Чтобы удалить приложение и K3s, выполните:
```bash
kubectl delete -f .k8s/
sudo /usr/local/bin/k3s-uninstall.sh
```
