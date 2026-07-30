# Sistema de Bienes Públicos

Este es un sistema de gestión de bienes públicos desarrollado con Django REST Framework.

## Instalación

1. Clona el repositorio
2. Crea un entorno virtual: `python -m venv venv`
3. Activa el entorno: `venv\Scripts\activate` (Windows)
4. Instala dependencias: `pip install -r requirements.txt`
5. Configura la base de datos en `core/settings.py`
6. Ejecuta migraciones: `python manage.py migrate`
7. Crea un superusuario: `python manage.py createsuperuser`
8. Ejecuta el servidor: `python manage.py runserver`

## APIs

### Autenticación

- POST `/api/login/` - Login con JWT
- POST `/api/token/refresh/` - Refrescar token

### Usuarios

- GET/POST/PUT/DELETE `/api/users/users/` - Gestión de usuarios

### Inventario

- GET/POST/PUT/DELETE `/api/inventario/sedes/` - Sedes
- GET/POST/PUT/DELETE `/api/inventario/unidades/` - Unidades administrativas
- GET/POST/PUT/DELETE `/api/inventario/ordenes/` - Órdenes de compra
- GET `/api/inventario/ordenes/{id}/reporte_pdf/` - Reporte PDF de orden
- GET/POST/PUT/DELETE `/api/inventario/catalogo/` - Catálogo de bienes
- GET/POST/PUT/DELETE `/api/inventario/bienes/` - Bienes públicos
- GET/POST/PUT/DELETE `/api/inventario/trazabilidad/` - Trazabilidad de movimientos

### Auditoría

- GET/POST/PUT/DELETE `/api/auditoria/auditoria/` - Registros de auditoría

## Pruebas

Ejecuta las pruebas con: `python manage.py test`

## Reportes PDF

Los reportes PDF se generan usando ReportLab. Ejemplo en `/api/inventario/ordenes/{id}/reporte_pdf/`

## Estructura del Proyecto

- `apps/users/` - Gestión de usuarios y autenticación
- `apps/inventario/` - Gestión de inventario y bienes
- `apps/auditoria/` - Auditoría del sistema
- `core/` - Configuración principal de Django
