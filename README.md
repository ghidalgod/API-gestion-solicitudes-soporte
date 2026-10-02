# Sistema de Gestión de Solicitudes de Soporte

API REST desarrollada con **Python, Django y Django REST Framework** para la gestión de solicitudes de soporte técnico.

El sistema permite a clientes registrar solicitudes, mientras que los agentes pueden gestionar su estado, asignaciones, comentarios internos e historial de cambios.

---

## 🚀 Tecnologías

- Python 3.13
- Django 5.2
- Django REST Framework 3.16+
- MySQL
- mysqlclient
- django-filter
- Token Authentication
- Postman

---

## 📋 Funcionalidades

### Usuarios y roles

El sistema implementa un esquema de autorización basado en roles, utilizando los permisos nativos de Django.

| Rol | Acceso | Principales acciones |
|:---:|---|---|
| 👤 **Cliente** | Solicitudes propias | Crear solicitudes, consultar sus tickets y modificar campos permitidos. |
| 🧑‍💻 **Agente** | Gestión de soporte | Consultar solicitudes, asignar agentes, cambiar estados, agregar comentarios internos y consultar historial. |
| 👑 **Administrador** | Administración | Gestionar usuarios y crear nuevos agentes, además de contar con las funcionalidades de agente. |

### 🔐 Identificación de roles

Los roles se identifican mediante los campos de Django:

| Rol | `is_staff` | `is_superuser` |
|---|:---:|:---:|
| Cliente | `False` | `False` |
| Agente | `True` | `False` |
| Administrador | `True` | `True` |

# 🎫 Gestión de solicitudes

Cada solicitud contiene:

* ID
* Asunto
* Descripción
* Prioridad
* Estado
* Cliente
* Agente asignado
* Fecha de creación
* Fecha de actualización

### Prioridades

- `LOW`
- `MEDIUM`
- `HIGH`

### Estados

- `OPEN`
- `IN_PROGRESS`
- `RESOLVED`

---
# 💬 Comentarios internos

Los agentes pueden agregar comentarios internos asociados a una solicitud.

Los comentarios contienen:

* ID
* Ticket
* Autor
* Texto
* Indicador de comentario interno
* Fecha de creación

Los endpoints de comentarios internos están restringidos a agentes.

---

# 📝 Historial de cambios

El sistema mantiene un historial de las modificaciones realizadas sobre las solicitudes.

El historial permite registrar:

* Solicitud modificada
* Campo modificado
* Valor anterior
* Nuevo valor
* Usuario que realizó la modificación
* Fecha y hora

---

# 🔐 Autenticación

La API utiliza **Token Authentication** de Django REST Framework.

Los endpoints protegidos requieren:

```http
Authorization: Token TU_TOKEN
```

El endpoint `POST /api/register/` crea un cliente y devuelve su token. El endpoint
`POST /api/agents/` también devuelve un token para el agente recién creado.
Incluir el token en las solicitudes protegidas en:

Header:

```http
Authorization: Token <token>
```

Caundo se usa POST/PATCH se debe agregar:
```http
content-type: application/json
```

---

# ⚙️ Instalación

* Se adjunta proyecto en el .zip

## 1. Clonar el proyecto

```bash
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DEL_PROYECTO>
```

---

## 2. Crear entorno virtual

En Windows:

```powershell
python -m venv venv
```

Activar:

```powershell
.\venv\Scripts\Activate.ps1
```

---

## 3. Instalar dependencias

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

# 🗄️ Configuración de MySQL

Crear la base de datos:

```sql
CREATE DATABASE support_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

Crear el usuario:

```sql
CREATE USER 'support_user'@'127.0.0.1'
IDENTIFIED BY 'TU_PASSWORD';
```

Asignar permisos:

```sql
GRANT ALL PRIVILEGES
ON support_db.*
TO 'support_user'@'127.0.0.1';
```

Aplicar cambios:

```sql
FLUSH PRIVILEGES;
```

---

# 🔑 Variables de entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
SECRET_KEY=REEMPLAZAR_POR_UNA_CLAVE_SEGURA
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=support_db
DB_USER=support_user
DB_PASSWORD=TU_PASSWORD
DB_HOST=127.0.0.1
DB_PORT=3306

TIME_ZONE=America/Santiago
```

Genera un valor para `SECRET_KEY` con:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

# 🧱 Migraciones

El repositorio incluye las migraciones necesarias. Aplicarlas con:

```bash
python manage.py migrate
```

```bash
python  manage.py makemigrations
```
---

# 👑 Crear administrador

```bash
python manage.py createsuperuser
```

El panel administrativo estará disponible en:

```text
http://127.0.0.1:8000/admin/
```

---

# ▶️ Ejecutar el proyecto

```bash
python manage.py runserver
```

La API estará disponible en:

```text
http://127.0.0.1:8000/api/
```

---

# 📡 Endpoints

## Registro de cliente

```http
POST /api/register/
```

Ejemplo:

```json
{
    "username": "cliente1",
    "first_name": "Juan",
    "last_name": "Pérez",
    "email": "juan@example.com",
    "password": "Password123"
}
```

---

## Crear agente

Solo un superusuario puede crear agentes.

```http
POST /api/agents/
```

Headers:

```http
Authorization: Token TOKEN_DEL_ADMIN
Content-Type: application/json
```

Body:

```json
{
    "username": "agente1",
    "first_name": "María",
    "last_name": "González",
    "email": "maria@empresa.com",
    "password": "Password123"
}
```

---

# 🎫 Tickets

## Listar tickets

```http
GET /api/tickets/
```

Los clientes solo pueden consultar sus propias solicitudes.

Los agentes pueden consultar las solicitudes para su gestión.

---

## Crear ticket

```http
POST /api/tickets/
```

Ejemplo:

```json
{
    "subject": "Problema con acceso al sistema",
    "description": "No puedo iniciar sesión.",
    "priority": "HIGH"
}
```

El cliente autenticado queda asociado automáticamente como propietario.

---

## Consultar ticket

```http
GET /api/tickets/{id}/
```
```http
Authorization: Token cliente o agente
```

Ejemplo:

```text
GET /api/tickets/4/
```

---

## Modificar ticket

```http
PATCH /api/tickets/{id}/
```

Ejemplo:

```json
{
    "subject": "Problema de acceso actualizado",
    "priority": "HIGH"
}
```

Los siguientes campos son de solo lectura mediante este endpoint:

```text
id
customer
assigned_agent
status
comments
created_at
updated_at
```

---

# 👨‍💻 Gestión de agentes

## Asignar agente

```http
PATCH /api/tickets/{id}/assign/
```

Ejemplo:

```json
{
    "agent_id": 3
}
```

Solo agentes autenticados pueden realizar esta operación.

---

## Cambiar estado

```http
PATCH /api/tickets/{id}/status/
```

Ejemplo:

```json
{
    "status": "IN_PROGRESS"
}
```

Solo agentes autenticados pueden cambiar el estado.

---

# 💬 Comentarios internos

## Crear comentario

```http
POST /api/tickets/{id}/comments/internal/
```

Ejemplo:

```json
{
    "text": "Se revisó la solicitud y se inició la gestión."
}
```

Solo agentes pueden crear comentarios internos.

---

## Consultar comentarios

```http
GET /api/tickets/{id}/comments/
```

Solo agentes pueden acceder a este endpoint.

---

# 📝 Historial

## Consultar historial

```http
GET /api/tickets/{id}/history/
```

Solo agentes pueden consultar el historial de modificaciones.

---

# 🗑️ Eliminación

Los clientes no pueden eliminar solicitudes.

Los agentes pueden eliminar solicitudes:

```http
DELETE /api/tickets/{id}/
```

Respuesta exitosa:

```text
204 No Content
```

---

# 🔒 Matriz de permisos

| Operación                      | Cliente | Agente | Administrador |
| ------------------------------ | :-----: | :----: | :-----------: |
| Registrarse                    |    ✅    |    -   |       -       |
| Crear ticket                   |    ✅    |    ✅   |       ✅       |
| Consultar propios tickets      |    ✅    |    ✅   |       ✅       |
| Consultar tickets para gestión |    ❌    |    ✅   |       ✅       |
| Modificar campos permitidos    |    ✅    |    ✅   |       ✅       |
| Asignar agente                 |    ❌    |    ✅   |       ✅       |
| Cambiar estado                 |    ❌    |    ✅   |       ✅       |
| Crear comentario interno       |    ❌    |    ✅   |       ✅       |
| Consultar comentarios internos |    ❌    |    ✅   |       ✅       |
| Consultar historial            |    ❌    |    ✅   |       ✅       |
| Eliminar ticket                |    ❌    |    ✅   |       ✅       |
| Crear agente                   |    ❌    |    ❌   |       ✅       |

---

# 🧪 Pruebas realizadas

La API fue probada mediante **Postman** y mediante las pruebas automatizadas de Django.

## Autenticación y usuarios

### Prueba 1 — Administrador crea agente

```text
POST /api/agents/
Resultado: 201 Created
```

### Prueba 2 — Agente intenta crear agente

```text
POST /api/agents/
Resultado: 403 Forbidden
```

Se confirma que únicamente un administrador puede crear agentes.

### Prueba 3 — Registro de cliente

```text
POST /api/register/
Resultado: 201 Created
```

---

# 🎫 Pruebas de tickets

### Prueba 4 — Cliente crea ticket

```text
POST /api/tickets/
Resultado: 201 Created
```

### Prueba 5 — Cliente consulta sus tickets

```text
GET /api/tickets/
Resultado: 200 OK
```

### Prueba 6 — Cliente intenta cambiar estado

```text
PATCH /api/tickets/{id}/status/
Resultado: 403 Forbidden
```

### Prueba 7 — Agente consulta tickets

```text
GET /api/tickets/
Resultado: 200 OK
```

### Prueba 8 — Agente asigna ticket

```text
PATCH /api/tickets/{id}/assign/
Resultado: 200 OK
```

### Prueba 9 — Agente cambia estado

```text
PATCH /api/tickets/{id}/status/
Resultado: 200 OK
```

### Prueba 10 — Agente crea comentario interno

```text
POST /api/tickets/{id}/comments/internal/
Resultado: 201 Created
```

### Prueba 11 — Agente consulta comentarios

```text
GET /api/tickets/{id}/comments/
Resultado: 200 OK
```

### Prueba 12 — Cliente intenta crear comentario interno

```text
POST /api/tickets/{id}/comments/internal/
Resultado: 403 Forbidden
```

### Prueba 13 — Cliente intenta consultar comentarios internos

```text
GET /api/tickets/{id}/comments/
Resultado: 403 Forbidden
```

### Prueba 14 — Agente consulta historial

```text
GET /api/tickets/{id}/history/
Resultado: 200 OK
```

### Prueba 15 — Cliente intenta consultar historial

```text
GET /api/tickets/{id}/history/
Resultado: 403 Forbidden
```

### Prueba 16 — Cliente intenta asignar agente

```text
PATCH /api/tickets/{id}/assign/
Resultado: 403 Forbidden
```

### Prueba 17 — Cliente intenta eliminar ticket

```text
DELETE /api/tickets/{id}/
Resultado: 403 Forbidden
```

### Prueba 18 — Agente elimina ticket

```text
DELETE /api/tickets/{id}/
Resultado: 204 No Content
```

### Prueba 19 — Verificación de ticket eliminado

```text
GET /api/tickets/{id}/
Resultado: 404 Not Found
```

---

# 🔐 Pruebas de seguridad y aislamiento

### Prueba 20 — Cliente intenta consultar ticket de otro cliente

```text
GET /api/tickets/{id}/
Resultado: 404 Not Found
```

Se confirma el aislamiento entre clientes.

### Prueba 21 — Cliente consulta su propio ticket

```text
GET /api/tickets/{id}/
Resultado: 200 OK
```

### Prueba 22 — Cliente modifica su propio ticket

```text
PATCH /api/tickets/{id}/
Resultado: 200 OK
```

### Prueba 23 — Usuario sin autenticación consulta tickets

```text
GET /api/tickets/
Resultado: 401 Unauthorized
```

### Prueba 24 — Cliente intenta eliminar su propio ticket

```text
DELETE /api/tickets/{id}/
Resultado: 403 Forbidden
```

---

# 🔄 Pruebas adicionales

### Prueba 25 — Agente consulta comentarios

```text
GET /api/tickets/{id}/comments/
Resultado: 200 OK
```

### Prueba 26 — Cliente intenta eliminar ticket propio

```text
DELETE /api/tickets/{id}/
Resultado: 403 Forbidden
```

### Prueba 27 — Agente cambia ticket a RESOLVED

```text
PATCH /api/tickets/{id}/status/
Resultado: 200 OK
```

### Prueba 28 — Verificación de historial

Se verificó que el cambio de estado quedara registrado.

```text
GET /api/tickets/{id}/history/
Resultado: 200 OK
```

### Prueba 29 — Agente intenta establecer el mismo estado

```text
PATCH /api/tickets/{id}/status/
Resultado: 400 Bad Request
```

Se evita realizar un cambio innecesario.

### Prueba 30 — Agente intenta reasignar el mismo agente

Resultado inicial:

```text
200 OK
```

Se detectó que se estaba generando un registro duplicado de historial.

Se corrigió la lógica de asignación.

### Pruebas 31 y 32 — Verificación de historial

Se comprobó la existencia de registros duplicados producidos por la asignación repetida.

### Prueba 33 — Reasignación del mismo agente después de la corrección

```text
PATCH /api/tickets/{id}/assign/
Resultado: 400 Bad Request
```

Mensaje:

```text
El agente ya está asignado a esta solicitud.
```

### Prueba 34 — Verificación de historial después de la corrección

Se confirmó que no se generó un nuevo registro de historial.

---

# ✅ Validaciones de datos

### Prueba 35 — Prioridad inválida

Se intentó crear un ticket con:

```text
URGENT
```

Resultado:

```text
400 Bad Request
```

### Prueba 36 — Ticket sin asunto

Resultado:

```text
400 Bad Request
```

### Prueba 37 — Ticket sin descripción

Resultado:

```text
400 Bad Request
```

### Prueba 38 — Ticket con prioridad LOW

```text
201 Created
```

### Prueba 39 — Ticket con prioridad MEDIUM

```text
201 Created
```

### Prueba 40 — Cliente intenta asignar agente directamente mediante PATCH

```json
{
    "assigned_agent": 3
}
```

Resultado:

```text
200 OK
```

La asignación no se modificó debido a que `assigned_agent` es `read_only`.

---

# 🔒 Validaciones finales de permisos

### Prueba 41 — Cliente intenta modificar estado directamente

```json
{
    "status": "RESOLVED"
}
```

Resultado:

```text
200 OK
```

El campo permaneció sin cambios debido a que `status` es `read_only`.

### Prueba 42 — Verificación del estado

El ticket permaneció:

```text
OPEN
```

### Prueba 43 — Cliente modifica prioridad

```json
{
    "priority": "HIGH"
}
```

Resultado:

```text
200 OK
```

### Prueba 44 — Verificación de prioridad

La prioridad quedó persistida:

```text
HIGH
```

### Prueba 45 — Cliente intenta modificar agente asignado

```json
{
    "assigned_agent": 3
}
```

Resultado:

```text
200 OK
```

El agente permaneció:

```text
null
```

La asignación debe realizarse mediante el endpoint específico de agentes.

### Prueba 46 — Cliente intenta eliminar solicitud propia

```text
DELETE /api/tickets/4/
Resultado: 403 Forbidden
```

### Prueba 47 — Cliente intenta consultar comentarios internos

```text
GET /api/tickets/4/comments/
Resultado: 403 Forbidden
```

### Prueba 48 — Cliente intenta consultar historial

```text
GET /api/tickets/4/history/
Resultado: 403 Forbidden
```

### Prueba 49 — Agente consulta solicitud

```text
GET /api/tickets/4/
Resultado: 200 OK
```

### Prueba 50 — Agente asigna solicitud

```text
PATCH /api/tickets/4/assign/
Resultado: 200 OK
```

### Prueba 51 — Verificación de agente asignado

Se confirmó que el agente quedó persistido:

```text
assigned_agent.id = 3
```

### Prueba 52 — Agente cambia estado

```text
PATCH /api/tickets/4/status/
Resultado: 200 OK
```

Estado:

```text
IN_PROGRESS
```

### Prueba 53 — Verificación del estado

Se confirmó que el estado quedó persistido:

```text
IN_PROGRESS
```

### Prueba 54 — Agente crea comentario interno

```text
POST /api/tickets/4/comments/internal/
Resultado: 201 Created
```

### Prueba 55 — Verificación del comentario

```text
GET /api/tickets/4/comments/
Resultado: 200 OK
```

El comentario quedó registrado correctamente.

---

# 📊 Paginación

Se verificó el endpoint:

```http
GET /api/tickets/
```

Durante las pruebas se obtuvo:

```json
{
    "count": 8,
    "next": null,
    "previous": null,
    "results": []
}
```

Esto confirmó el funcionamiento de la paginación y el conteo de solicitudes.

Posteriormente, los datos utilizados durante las pruebas fueron eliminados para dejar la base de datos limpia.

---

# 🧹 Limpieza de datos de prueba

Los usuarios y tickets de desarrollo pertenecen a la base de datos local y no se
incluyen en el repositorio. Crea tus propios datos de prueba en cada entorno.

---

# 🧪 Tests automatizados

Los tests automatizados de Django fueron ejecutados mediante:

```bash
python manage.py test
```

Resultado validado:

```text
Found 6 test(s)

System check identified no issues

......

OK
```

Resultado:

```text
6/6 tests aprobados
```

---

# ⚡ Optimización

El proyecto utiliza `select_related()` y `prefetch_related()` para optimizar las consultas relacionadas.

Ejemplo:

```python
Ticket.objects.select_related(
    "customer",
    "assigned_agent"
).prefetch_related(
    "comments__author"
)
```

Esto permite reducir consultas innecesarias a la base de datos al recuperar información relacionada.

---

# 📁 Estructura del proyecto

```text
.
├── .gitignore
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── README.md
├── requirements.txt
├── .env
└── tickets/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── migrations/
    │   ├── __init__.py
    │   └── 0001_initial.py
    ├── models.py
    ├── permissions.py
    ├── serializers.py
    ├── signals.py
    ├── tests.py
    ├── urls.py
    └── views.py
```

---

# 🛠️ Comandos útiles

### Verificar configuración

```bash
python manage.py check
```

### Ejecutar servidor

```bash
python manage.py runserver
```

### Crear migraciones

```bash
python manage.py makemigrations
```

### Aplicar migraciones

```bash
python manage.py migrate
```

### Ejecutar tests

```bash
python manage.py test
```

### Crear superusuario

```bash
python manage.py createsuperuser
```

### Crear token

```bash
python manage.py drf_create_token usuario
```

---

# 📮 Pruebas con Postman

Las pruebas manuales fueron realizadas utilizando Postman, verificando:

* Autenticación.
* Autorización.
* Roles.
* Registro de usuarios.
* Creación de agentes.
* Creación de tickets.
* Consulta de tickets.
* Aislamiento entre clientes.
* Asignación de agentes.
* Cambio de estados.
* Comentarios internos.
* Historial.
* Validación de datos.
* Eliminación.
* Paginación.
* Restricciones de acceso.

---

# 👩‍💻 Autora

**Gabriela Hidalgo**

Proyecto desarrollado como prueba técnica para demostrar conocimientos en:

* Python
* Django
* Django REST Framework
* APIs REST
* MySQL
* Autenticación y autorización
* Diseño de APIs
* Backend
* Testing
* Optimización de consultas
* Control de acceso basado en roles


