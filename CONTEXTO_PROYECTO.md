# SUDEVIP — Sistema de Bienes Públicos DEM
## Contexto completo del proyecto para continuación

---

## ¿Qué es este proyecto?

Sistema web de gestión de bienes públicos para la **Dirección Ejecutiva de la Magistratura (DEM)**. Permite registrar, asignar y administrar bienes (automotores e inmuebles), gestionando usuarios, órdenes de compra y asignaciones a funcionarios.

**Repositorio:** https://github.com/figudieg/bienes

---

## Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend | Django 5.2 + Django REST Framework + simplejwt |
| Base de datos | PostgreSQL 15 |
| Frontend | Angular 19 (standalone components) |
| Template UI | Phoenix v1.24.0 (Bootstrap 5) |
| Íconos | Font Awesome (modo JS/SVG — `all.min.js`) |
| PDF | ReportLab (Python) |
| Autenticación | JWT (access + refresh tokens) |

---

## Estructura de carpetas

```
sistemas/
├── backend/                  # Django project
│   ├── config/               # settings.py, urls.py, wsgi
│   ├── apps/
│   │   ├── inventario/       # Modelos core: Bien, Sede, Area, OrdenCompra, Asignacion
│   │   ├── automotor/        # Modelo Automotor (hereda de Bien)
│   │   ├── inmuebles/        # Modelo Inmueble (hereda de Bien)
│   │   ├── auditoria/        # Logs de acceso y trazabilidad
│   │   └── usuarios/         # Modelo User personalizado
│   └── manage.py
├── frontend/                 # Angular 19
│   └── src/app/
│       ├── core/             # services/, guards/, models/
│       ├── features/         # módulos por funcionalidad
│       └── shared/           # sidebar, navbar, componentes comunes
├── scripts/
│   └── bienes_dump.sql       # Dump PostgreSQL con datos de prueba
├── .env                      # Variables de entorno (NO subir a git — ya en .gitignore)
└── .env.example              # Plantilla de variables
```

---

## Cómo levantar el proyecto

### 1. Variables de entorno

Crear `.env` en la raíz con:

```env
SECRET_KEY=tu_secret_key_django
DEBUG=True
DB_NAME=bienes
DB_USER=postgres
DB_PASSWORD=123
DB_HOST=localhost
DB_PORT=5432
```

### 2. Backend

```bash
# Activar entorno virtual
C:\Users\Admin\Documents\entorno\bienes\Scripts\activate

# Ir al backend
cd backend

# Instalar dependencias (si es primera vez)
pip install -r requirements.txt

# Aplicar migraciones
python manage.py migrate

# Restaurar datos de prueba (opcional)
psql -U postgres -d bienes -f ../scripts/bienes_dump.sql

# Levantar servidor
python manage.py runserver
```

> **Importante:** Si PostgreSQL devuelve errores en español con caracteres raros (UnicodeDecodeError), ejecutar en DBeaver:
> ```sql
> ALTER SYSTEM SET lc_messages = 'C';
> SELECT pg_reload_conf();
> ```
> Luego reiniciar el servicio PostgreSQL.

### 3. Frontend

```bash
cd frontend
npm install   # solo primera vez
ng serve
```

App disponible en: `http://localhost:4200`

---

## Usuarios del sistema (datos de prueba)

| Username | Contraseña | Rol |
|----------|-----------|-----|
| admin | (definida al crear superuser) | ADMINISTRADOR |
| martidiaz | (definida al migrar) | ADMINISTRADOR |
| operador | (definida al migrar) | OPERADOR |
| auditor | (definida al migrar) | AUDITOR |

**Para crear superuser desde cero:**
```bash
python manage.py createsuperuser
```
Luego asignar rol ADMINISTRADOR desde Django shell:
```python
python manage.py shell
from apps.usuarios.models import Usuario
u = Usuario.objects.get(username='admin')
u.rol = 'ADMINISTRADOR'
u.save()
```

---

## Roles y permisos

| Rol | Puede |
|-----|-------|
| ADMINISTRADOR | Todo: CRUD completo, eliminar registros, gestión de usuarios |
| OPERADOR | Crear y editar bienes, automotores, inmuebles, asignaciones |
| AUDITOR | Solo lectura + acceso a reportes y órdenes de compra |

**Regla clave en backend:** El permiso `IsAdminOrReadWrite` (definido en cada `views.py`) restringe el método `DELETE` exclusivamente al rol ADMINISTRADOR. Está implementado en:
- `apps/inventario/views.py`
- `apps/automotor/views.py`
- `apps/inmuebles/views.py`

---

## Módulos del frontend

### Activos

| Módulo | Ruta | Acceso |
|--------|------|--------|
| Panel Principal | `/inicio` | Todos |
| Registro de Bienes | `/bienes` | Todos |
| Lista de Bienes | `/bienes/lista` | Todos |
| Asignaciones | `/asignaciones` | OPERADOR, ADMINISTRADOR |
| Nueva Asignación | `/asignaciones/nueva` | OPERADOR, ADMINISTRADOR |
| Automotores | `/automotor` | Todos |
| Registro Automotor | `/automotor/nuevo` | OPERADOR, ADMINISTRADOR |
| Editar Automotor | `/automotor/editar/:id` | OPERADOR, ADMINISTRADOR |
| Inmuebles | `/inmuebles` | Todos |
| Registro Inmueble | `/inmuebles/nuevo` | OPERADOR, ADMINISTRADOR |
| Editar Inmueble | `/inmuebles/editar/:id` | OPERADOR, ADMINISTRADOR |
| Órdenes de Compra | `/ordenes` | AUDITOR, ADMINISTRADOR |
| Reportes SUDEBIN | `/inicio/sudebin-reportes` | AUDITOR, ADMINISTRADOR |
| Gestión de Usuarios | `/inicio/gestion-usuarios` | ADMINISTRADOR |

### Comentados (pendientes, no eliminar)

- **Auditoría e Histórico** — comentado en `sidebar.ts` y `inicio.html`
- **Buzón de Recuperaciones** — comentado en `sidebar.ts`

Para reactivarlos, descomentar en:
- `frontend/src/app/shared/components/sidebar/sidebar.ts` (el item del menú)
- `frontend/src/app/features/dashboard/inicio.html` (el botón de gestión rápida)

---

## Modelos de base de datos clave

### Bien (tabla base — herencia multi-tabla)
```
id, nombre, descripcion, codigo_inventario, serial_fabrica (nullable/unique),
estado (ACTIVO/INACTIVO/DESINCORPORADO), sede_id, orden_compra_id,
valor_adquisicion, tasa_bcv_compra, valor_adquisicion_bs, fecha_registro
```

### Automotor (extiende Bien)
```
placa (unique), marca, modelo, anio, color,
serial_motor (nullable/unique), serial_carroceria (nullable/unique),
tipo_vehiculo, kilometraje
```

### Inmueble (extiende Bien)
```
catastro (unique), direccion_completa, registro_propiedad,
area_terreno, area_construccion, valor_adquisicion (override)
```

### Asignacion
```
bien_id, usuario_id, area_id, fecha_asignacion, activa (boolean)
```
**Regla:** Un bien solo puede tener UNA asignación `activa=True` a la vez.
Si se intenta asignar un bien ya activo, el backend devuelve error 400.

---

## Datos pre-cargados (en dump)

- **Sede:** Sede Principal DEM
- **Áreas:** Dirección General, Recursos Humanos, Administración y Finanzas, Tecnología de Información, Servicios Generales, Seguridad
- **3 bienes de prueba** (1 automotor, 1 inmueble, 1 bien general)
- **3 asignaciones** (1 activa, 2 inactivas — del mismo inmueble DEM-INM-5716)
- **1 orden de compra**
- **4 usuarios** (ver tabla arriba)

---

## Decisiones técnicas importantes

### Serial único nullable
Los campos `serial_fabrica`, `serial_motor`, `serial_carroceria` son `unique=True` en la BD pero **nullable**. Si el frontend envía string vacío `""`, los serializers lo convierten a `None` para evitar violación de constraint único. Esto está implementado con `validate_<campo>` en:
- `apps/inventario/serializers.py` → `BienSerializer`
- `apps/automotor/serializers.py` → `AutomotorSerializer`
- `apps/inmuebles/serializers.py` → `InmuebleSerializer`

### Font Awesome sin duplicación de íconos
FA está en modo JS/SVG (`all.min.js`). Cuando Angular re-renderiza un componente, FA inyectaba el SVG dos veces. Fix en `index.html`:
```html
<script>window.FontAwesomeConfig = { autoReplaceSvg: 'nest' };</script>
```

### Gestión de usuarios — modal con *ngIf
El modal de crear/editar usuario usa `*ngIf="modalAbierto"` (NO `[style.display]`). Esto es intencional: Bootstrap dejaba el `.modal` en el DOM como overlay invisible bloqueando clics en la tabla. Con `*ngIf` se elimina completamente del DOM al cerrar.

### Búsqueda en gestión de usuarios
El input de búsqueda tiene `type="search"`, `autocomplete="off"`, y en `ngAfterViewInit` hay un `setTimeout(200ms)` que resetea `searchQuery = ''` para evitar que el autocompletado del browser rellene el campo con el email del usuario y filtre la lista vacía.

---

## Endpoints API principales

Base URL: `http://localhost:8000/api/`

| Endpoint | Métodos |
|----------|---------|
| `inventario/bienes/` | GET, POST, PUT, DELETE |
| `inventario/asignaciones/` | GET, POST, DELETE |
| `inventario/sedes/` | GET, POST |
| `inventario/areas/` | GET, POST |
| `inventario/ordenes/` | GET, POST |
| `automotores/` | GET, POST, PUT, DELETE |
| `inmuebles/` | GET, POST, PUT, DELETE |
| `gestion/` | GET (lista usuarios) |
| `gestion/<id>/` | PUT, DELETE (editar/eliminar usuario) |
| `auth/token/` | POST (login → access + refresh) |
| `auth/token/refresh/` | POST |

---

## Pendientes / Mejoras futuras

- [ ] Reactivar módulo **Auditoría e Histórico**
- [ ] Reactivar módulo **Buzón de Recuperaciones**
- [ ] Agregar `unidad_pertenencia` (área) a los usuarios desde Gestión de Usuarios
- [ ] Reportes PDF más completos
- [ ] Paginación en listas grandes

---

## Notas de configuración del entorno Windows

- Entorno virtual Python: `C:\Users\Admin\Documents\entorno\bienes\`
- PostgreSQL 15 instalado en: `C:\Program Files\PostgreSQL\15\`
- Para hacer dump manual:
  ```powershell
  $env:PGPASSWORD="123"; & "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe" -U postgres -h localhost -d bienes -F p -f "scripts\bienes_dump.sql"
  ```
- Servicio PostgreSQL: `postgresql-x64-15` (reiniciar con `Restart-Service -Name postgresql-x64-15` en PowerShell Admin)
