# 🤬 InsultService & InsultFilter 🚫

Este repositorio contiene implementaciones de los servicios **InsultService** e **InsultFilter** utilizando diferentes tecnologías de comunicación: XMLRPC, Pyro4, Redis y RabbitMQ. También incluye scripts para ejecutar tests y pruebas de rendimiento.

---

## ⚙️ Ejecución

### 🛠️ XMLRPC

- Ejecutar el servidor **InsultService**:

  ```bash
  python3 xmlrpc/insult_service.py
  ```

- Ejecutar el servidor **InsultFilter**:

  ```bash
  python3 xmlrpc/insult_filter.py
  ```

- Ejecutar los tests:

  ```bash
  python3 tests/xmlrpc/test1.py
  ```

---

### 🔥 Pyro4

- Iniciar el Name Server de Pyro4 (necesario para registrar y localizar objetos remotos):

  ```bash
  python3 -m Pyro4.naming
  ```

- Ejecutar el servidor **InsultService**:

  ```bash
  python3 pyro/insult_service.py
  ```

- Ejecutar el servidor **InsultFilter**:

  ```bash
  python3 pyro/insult_filter.py
  ```

- Ejecutar los tests de rendimiento:

  ```bash
  python3 tests/pyro/test1.py
  ```

---

### 🐹 Redis

- Descargar y ejecutar Redis con Docker:

  ```bash
  docker pull redis
  docker run --name my-redis -d -p 6379:6379 redis
  ```

- Ejecutar los tests:

  ```bash
  python3 tests/redis/test_redis_[nombre].py
  ```

---

### 🐰 RabbitMQ

- Descargar y ejecutar RabbitMQ con Docker:

  ```bash
  docker pull rabbitmq:management
  docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management
  ```

- Ejecutar los tests:

  ```bash
  python3 tests/rabbitmq/test_rabbitmq_[nombre].py
  ```

---

## 📝 Notas

- Cambia `[nombre]` por el nombre específico del test que quieres ejecutar en Redis o RabbitMQ.
