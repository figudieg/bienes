# Sistema de Bienes Públicos DEM
## Contexto completo del proyecto para continuación

> Este documento describe **qué es** el proyecto y cómo está armado hoy. Para el detalle cronológico de qué cambió recientemente y qué falta, ver [`CAMBIOS_RECIENTES.md`](CAMBIOS_RECIENTES.md).

---

## ¿Qué es este proyecto?

Sistema web de gestión de bienes públicos para la **Dirección Ejecutiva de la Magistratura (DEM)**. Permite registrar, asignar y administrar bienes (muebles, automotores e inmuebles), llevar el historial de incorporación/reasignación/desincorporación, generar los documentos oficiales en PDF (comprobantes, fichas, reportes) y gestionar las cuentas de quienes operan el sistema (Bienes Públicos).

**Repositorio:** https://github.com/figudieg/bienes

---

## Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend | Django 5.2 + Django REST Framework + simplejwt |
| Base de datos | PostgreSQL |
| Frontend | Angular 21 (standalone components) |
| Template UI | Phoenix (Bootstrap 5) |
| Íconos | Font Awesome (modo JS/SVG — `all.min.js`) |
| PDF | ReportLab (Python) |
| Excel | pandas + openpyxl (.xlsx) + xlrd (.xls) |
| Autenticación | JWT (access + refresh tokens) |

---

## Estructura de carpetas

```
bienes/
├── backend/                      # Django project
│   ├── config/                   # settings.py, urls.py, wsgi
│   ├── apps/
│   │   ├── users/                 # CustomUser (login, roles) — NO es Funcionario
│   │   ├── inventario/            # Bien, Sede, Area, Funcionario, OrdenCompra, Asignacion, Trazabilidad, Mantenimiento
│   │   ├── automotor/             # Automotor (hereda de Bien, herencia multi-tabla)
│   │   ├── inmuebles/             # Inmueble (hereda de Bien, herencia multi-tabla)
│   │   └── auditoria/             # LogBien, LogAcceso
│   ├── .env                      # Variables de entorno (NO se sube a git)
│   ├── .env.example              # Plantilla — copiar a .env y completar
│   └── manage.py
├── frontend/                     # Angular
│   ├── src/app/
│   │   ├── core/                 # services/, guards/, models/
│   │   ├── features/             # módulos por funcionalidad
│   │   └── shared/                # sidebar, navbar, gestion-bien-modal, componentes comunes
│   ├── scripts/set-env.js        # Genera src/environments/environment.ts a partir de frontend/.env
│   ├── .env                      # API_URL, PRODUCTION (NO se sube a git)
│   └── .env.example
├── scripts/
│   ├── convalidacion_oficinas.xls  # Fuente del directorio real de oficinas del DEM (import_oficinas)
│   └── deploy/
│       └── diagnostico_servidor.sh # Diagnóstico de solo lectura para el servidor de calidad
├── docs/
│   └── guia-desarrollo.md        # Notas de planificación históricas
└── CAMBIOS_RECIENTES.md          # Changelog vivo del proyecto
```

---

## Cómo levantar el proyecto

### 1. Backend

```bash
cd backend
# activar el entorno virtual que corresponda
pip install -r requirements.txt

cp .env.example .env
# completar backend/.env: DB_*, DJANGO_SECRET_KEY, WSSISCOM_EVALUACION_URL, etc.

python manage.py migrate
python manage.py seed_users        # crea admin / auditor / operador de prueba
python manage.py runserver 0.0.0.0:8000
```

> **`backend/.env`** — antes vivía en la raíz del repo; se movió aquí para ser simétrico con `frontend/.env` (`load_dotenv()` en `settings.py` apunta a `BASE_DIR / '.env'`). Si `DEBUG=True` con datos incompletos, Django puede arrancar con valores por defecto inseguros — revisar siempre que las variables clave (`DB_*`, `DJANGO_SECRET_KEY`) estén completas.

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env
# editar frontend/.env: API_URL debe apuntar al backend real (host:puerto)
npm start
```

> **`frontend/.env`** define `API_URL` (a qué backend le habla el frontend) y `PRODUCTION` (`true` solo al compilar para el servidor de calidad/producción). `npm start` y `npm run build` regeneran automáticamente `src/environments/environment.ts` a partir de este archivo (vía `scripts/set-env.js`, enganchado como `prestart`/`prebuild` en `package.json`) — **no editar `environment.ts` a mano**, se sobrescribe en cada arranque/build.

App disponible en: `http://localhost:4200` (o el host/puerto que se le indique a `ng serve --host`).

---

## Usuarios del sistema (datos de prueba)

Creados por `python manage.py seed_users`:

| Username | Contraseña | Rol |
|----------|-----------|-----|
| admin | `Password123!` | ADMINISTRADOR (superuser) |
| auditor | `Password123!` | AUDITOR |
| operador | `Password123!` | OPERADOR |

**Importante:** estas cuentas (`CustomUser`) son para el **personal de Bienes Públicos que opera el sistema**. Son completamente distintas de `Funcionario` (el directorio de personas a quienes se les asignan bienes) — `Funcionario` no tiene login y se alimenta desde SISCOM, no desde esta tabla.

---

## Roles y permisos

| Rol | Puede |
|-----|-------|
| ADMINISTRADOR | Todo: CRUD completo, eliminar registros, gestión de usuarios |
| OPERADOR | Crear y editar bienes, automotores, inmuebles, asignaciones |
| AUDITOR | Solo lectura + acceso a reportes, auditoría y órdenes de compra |

**Regla clave en backend:** el permiso `IsAdminOrReadWrite` restringe el método `DELETE` exclusivamente al rol ADMINISTRADOR. Implementado en `apps/inventario/views.py`, `apps/automotor/views.py`, `apps/inmuebles/views.py`.

---

## Módulos del frontend (todos activos)

| Módulo | Ruta | Acceso |
|--------|------|--------|
| Panel Principal | `/inicio` | Todos |
| Registro de Bienes | `/bienes` | Todos |
| Asignaciones | `/asignaciones` | OPERADOR, ADMINISTRADOR |
| Perfil de Funcionario | `/asignaciones/perfil` | OPERADOR, ADMINISTRADOR |
| Automotores | `/automotor` | Todos |
| Inmuebles | `/inmuebles` | Todos |
| Órdenes de Compra | `/ordenes` | AUDITOR, ADMINISTRADOR |
| Auditoría e Histórico | `/auditoria` | AUDITOR, ADMINISTRADOR |
| Reportes de Bienes Públicos | `/inicio/reportes-bienes-publicos` | AUDITOR, ADMINISTRADOR |
| Buzón de Recuperaciones | `/inicio/bandeja-recuperacion` | ADMINISTRADOR |
| Gestión de Usuarios | `/inicio/gestion-usuarios` | ADMINISTRADOR |

---

## Modelos de base de datos clave

### Bien (tabla base — herencia multi-tabla)
```
id, nombre, descripcion, codigo_inventario (unique), serial_fabrica (nullable/unique),
estado (ACTIVO/INACTIVO/DESINCORPORADO),
categoria (nullable — solo aplica a muebles: COMPUTADORA/PANTALLA/PERIFERICO/
           MOBILIARIO/EQUIPO_OFICINA/ELECTRODOMESTICO/HERRAMIENTA/OTRO),
sede_id, orden_compra_id (nullable),
valor_adquisicion, tasa_bcv_compra, valor_adquisicion_bs
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
area_terreno, area_construccion
```

### Funcionario (directorio de personas — sin login)
```
cedula (unique), nombres, apellidos, cargo, area_id (nullable)
```
Se crea/actualiza automáticamente al consultar una cédula vía SISCOM (`consultar-cedula`). No hay pantalla para crearlo a mano — es una decisión de diseño, no un pendiente.

### Area
```
nombre, sede_id, codigo (nullable, ej. "03-14"), direccion_general (nullable),
activa (boolean — oficinas cerradas)
```

### Asignacion
```
bien_id, funcionario_id (nullable), area_id, fecha_asignacion, activa (boolean)
```
**Regla:** un bien solo puede tener UNA asignación `activa=True` a la vez. Si se intenta asignar un bien que ya tiene una asignación activa, el backend devuelve 400 (`AsignacionSerializer.validate_bien`).

### TrazabilidadMovimientos (histórico)
```
bien_id, tipo_movimiento (INCORPORACION/ASIGNACION/REASIGNACION/DESINCORPORACION),
sede_origen_id, sede_destino_id, area_origen_id, area_destino_id,
funcionario_origen_id, funcionario_destino_id, fecha, motivo, usuario_responsable_id
```

### MantenimientoBien
```
bien_id, numero_ficha, fecha_ficha, tipo_mantenimiento (PREVENTIVO/CORRECTIVO),
actividad_realizada, materiales_empleados, numero_factura, costo,
fecha_mantenimiento, reparado_por, conformado_por, responsable_administrativo, nota
```

### OrdenCompra
```
numero_orden (unique), proveedor, fecha_llegada, conformidad_recepcion,
archivo_documento (obligatorio — Bienes Públicos solo carga la orden, no la origina)
```

---

## Decisiones técnicas importantes

### `Funcionario` vs `CustomUser`
Son dos tablas completamente separadas a propósito. `CustomUser` = personal de Bienes Públicos que usa el sistema (login, roles). `Funcionario` = cualquier persona del DEM a quien se le puede asignar un bien (sin login, sincronizado desde SISCOM). No unificar estas tablas.

### Herencia multi-tabla (`Bien` → `Automotor`/`Inmueble`) y señales de Django
Guardar una instancia de `Automotor` o `Inmueble` dispara `post_save` con `sender=Automotor`/`sender=Inmueble`, **no** `sender=Bien`. Cualquier señal que necesite reaccionar a cambios en cualquier tipo de bien debe registrarse para los tres senders (ver `apps/auditoria/models.py`, `registrar_auditoria_bien`).

### Serial único nullable
Los campos `serial_fabrica`, `serial_motor`, `serial_carroceria` son `unique=True` en la BD pero **nullable**. Si el frontend envía `""`, los serializers lo convierten a `None` para evitar violación de constraint único (`validate_<campo>` en `BienSerializer`/`AutomotorSerializer`/`InmuebleSerializer`).

### Reasignar / Desincorporar: individual y masivo comparten lógica
`BienViewSet._reasignar_bien` / `_desincorporar_bien` (privados) contienen la lógica real; tanto los endpoints individuales (`bienes/{id}/reasignar/`, `bienes/{id}/desincorporar/`) como los masivos (`bienes/reasignar-masivo/`, `bienes/desincorporar-masivo/`) los reutilizan. Si se toca esta lógica, tocar un solo lugar.

### `.env` por aplicación, no compartido
`backend/.env` y `frontend/.env` son independientes, cada uno gitignorado con su `.env.example` como plantilla commiteada. El frontend nunca debe tener secretos de base de datos ni de backend — todo lo que termina en `environment.ts` es público (se compila al bundle JS que baja cualquier navegador).

### Font Awesome sin duplicación de íconos
FA está en modo JS/SVG (`all.min.js`). Cuando Angular re-renderiza un componente, FA inyectaba el SVG dos veces. Fix en `index.html`:
```html
<script>window.FontAwesomeConfig = { autoReplaceSvg: 'nest' };</script>
```

### Gestión de usuarios — modal con `*ngIf`
El modal de crear/editar usuario usa `*ngIf="modalAbierto"` (NO `[style.display]`). Bootstrap dejaba el `.modal` en el DOM como overlay invisible bloqueando clics en la tabla. Con `*ngIf` se elimina completamente del DOM al cerrar.

---

## Endpoints API principales

Base URL: `{API_URL de frontend/.env}` (por defecto en desarrollo, `http://localhost:8000/api/`)

| Endpoint | Métodos |
|----------|---------|
| `inventario/bienes/` | GET, POST, PUT, DELETE |
| `inventario/bienes/{id}/reasignar/` | POST (individual, devuelve PDF) |
| `inventario/bienes/{id}/desincorporar/` | POST (individual, devuelve PDF) |
| `inventario/bienes/reasignar-masivo/` | POST (devuelve PDF) |
| `inventario/bienes/desincorporar-masivo/` | POST (devuelve PDF) |
| `inventario/bienes/mantenimiento-masivo/` | POST (devuelve PDF) |
| `inventario/bienes/importar-excel/` | POST |
| `inventario/bienes/inventario-general-pdf/` | GET (filtros por query params) |
| `inventario/asignaciones/` | GET, POST, DELETE |
| `inventario/funcionarios/` | GET |
| `inventario/funcionarios/buscar-por-cedula/` | GET (respaldo local, sin SISCOM) |
| `inventario/funcionarios/{id}/perfil/` | GET (bienes asignados a ese funcionario) |
| `inventario/sedes/` | GET, POST |
| `inventario/areas/` | GET, POST |
| `inventario/ordenes/` | GET, POST |
| `inventario/trazabilidad/` | GET |
| `inventario/mantenimientos/` | GET |
| `automotor/` | GET, POST, PUT, DELETE |
| `inmuebles/` | GET, POST, PUT, DELETE |
| `users/gestion/` | GET (lista), POST (crear) |
| `users/gestion/{id}/` | PUT, DELETE |
| `users/gestion/consultar-cedula/` | GET (SISCOM, solo red del DEM) |
| `users/auth/login/` | POST (username + password → access + refresh) |
| `auditoria/logs/` | GET |
| `auditoria/accesos/` | GET |

---

## Pendientes / Mejoras futuras

- [ ] `tests.py` de `inventario` roto/desactualizado — reescribir contra el esquema actual con `Funcionario`.
- [ ] Excel masivo de bienes (importación completa) — estrategia sin definir, en pausa.
- [ ] Endpoints masivos devuelven solo el PDF, sin JSON de resumen — evaluar si conviene agregarlo.
- [ ] Campos del formato oficial de PDF sin capturar aún (condición física, RIF proveedor, control perceptil, disponibilidad presupuestaria).
- [ ] Paginación en listas grandes.
- [ ] Despliegue en el servidor de calidad (`172.26.97.36`) — configuración ya preparada en `.env`, falta correr `scripts/deploy/diagnostico_servidor.sh` ahí y armar Gunicorn + Nginx + systemd (backend pensado para el puerto 9005).

---

## Notas de configuración del entorno de desarrollo (Windows)

- El `.env` de cada app vive dentro de su carpeta (`backend/.env`, `frontend/.env`), no en la raíz del repo.
- Para levantar backend y frontend juntos en Claude Code, ver `.claude/launch.json`.
- Comando para dejar la base de datos limpia (bienes/asignaciones/funcionarios), preservando usuarios/Sedes/Áreas:
  ```bash
  python manage.py reset_datos_prueba --yes
  ```
