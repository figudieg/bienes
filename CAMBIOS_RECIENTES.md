# Estado del Proyecto — Sistema de Bienes Públicos DEM (SUDEVIP)

> **Última actualización:** 20 Ago 2026
> Todavía **sin commitear** — hay mucho trabajo desde el último commit (`047ba5d`). Revisar `git status` antes de seguir.

---

## Resumen ejecutivo

Desde el último commit se hicieron **cuatro bloques grandes de trabajo**:

1. **Cambio de arquitectura: `Funcionario` reemplaza a `usuario` en Asignaciones.** Ahora las personas a quienes se les asignan bienes NO necesitan cuenta de login — son un directorio propio (`Funcionario`), separado de las cuentas del sistema (`CustomUser`, que son solo para el personal de Bienes Públicos que opera el sistema).
2. **Directorio real de oficinas del DEM cargado como `Area`** (53 oficinas reales, con código, dirección general y estado activo/cerrado), reemplazando las 6 áreas genéricas de prueba.
3. **Integración con SISCOM (wssiscom.dem.int)** para traer datos frescos del funcionario por cédula, con:
   - Auto-creación/sincronización del `Funcionario` local en cada consulta.
   - Matching automático de la oficina (texto libre de SISCOM → `Area` real).
   - Respaldo local automático cuando SISCOM no responde (fuera de la red del DEM).
4. **Nueva pantalla "Perfil de Funcionario"** que resuelve el problema de ver los bienes de una persona repetidos en la lista de asignaciones.

También se rediseñó el módulo de Reportes SUDEBIN (estilo + filtros), se generaron los PDFs con el formato oficial del DEM, y se ajustó Órdenes de Compra para que sea solo carga/constancia, no creación.

---

## Cómo levantar el proyecto (en una máquina nueva)

```bash
# 1. Backend
cd backend
python -m venv venv        # o el venv que ya tengas
venv\Scripts\activate
pip install -r requirements.txt   # incluye pandas/openpyxl/xlrd ahora

# 2. Variables de entorno — crear .env en la raíz del repo (NO se commitea)
# copiar .env.example y completar DB_PASSWORD, WSSISCOM_EVALUACION_URL, etc.

# 3. Base de datos (Postgres). Si es una BD nueva:
python manage.py migrate

# 4. Frontend
cd ../frontend
npm install
# crear src/environments/environment.ts (NO se commitea):
#   export const environment = { production: false, apiUrl: 'http://localhost:8000/api' };
ng serve
```

> **Nota de red:** el endpoint de consulta de funcionario por cédula (`consultar-cedula`) depende de `wssiscom.dem.int`, solo accesible **dentro de la red del DEM**. Fuera de esa red vas a ver error 502 — es esperado. Para eso existe el respaldo local (ver más abajo).

> **Si el proyecto ya tiene datos de una sesión anterior con el modelo viejo** (`Asignacion.usuario` en vez de `Asignacion.funcionario`), correr las migraciones puede fallar o dejar `funcionario_id` en NULL en filas viejas — es un cambio de esquema, no hay forma de migrar los datos automáticamente. Ver comando `reset_datos_prueba` más abajo.

---

## Cambios de fondo (backend)

### `apps/inventario/models.py`

- **Nuevo modelo `Funcionario`**: `cedula` (única), `nombres`, `apellidos`, `cargo`, `area` (FK opcional). Sin login, sin relación con `CustomUser`.
- **`Asignacion.funcionario`** reemplaza a `Asignacion.usuario`. Igual en `TrazabilidadMovimientos` (`funcionario_origen`/`funcionario_destino`).
- **`Area` ampliada**: `codigo` (ej. `"03-14"`), `direccion_general` (agrupación, ej. `"DIRECCIÓN GENERAL DE ADMINISTRACIÓN Y FINANZAS"`), `activa` (boolean, para oficinas cerradas).
- **`OrdenCompra.archivo_documento`** ahora es **obligatorio** (antes opcional) — refleja que Bienes Públicos solo carga la orden ya emitida por otra dependencia, no la origina.

### `apps/inventario/management/commands/`
- **`import_oficinas.py`** — importa el Excel de Convalidación de Oficinas (`scripts/convalidacion_oficinas.xls`, ya copiado al repo) como registros de `Area`. Reusar si llega una versión actualizada del Excel:
  ```bash
  python manage.py import_oficinas
  ```
- **`reset_datos_prueba.py`** — limpia bienes/asignaciones/funcionarios/trazabilidad/mantenimientos/órdenes de compra, **preservando** cuentas de usuario, Sedes y Áreas. Útil para volver a probar el flujo desde cero:
  ```bash
  python manage.py reset_datos_prueba --yes
  ```

### `apps/users/views.py` — `consultar-cedula`
`GET /api/users/gestion/consultar-cedula/?cedula=<número>`
- Consulta SISCOM, y **crea o actualiza** el `Funcionario` local (cédula, nombres/apellidos —partidos del nombre completo que da SISCOM—, cargo).
- Intenta emparejar la `dependencia` de SISCOM (texto libre, sin tildes) contra el nombre real de alguna `Area` cargada, y si hay match, actualiza `Funcionario.area`.
- Devuelve `funcionario_id` listo para usar en una Asignación.
- **No hay respaldo local en este endpoint** — si SISCOM no responde, devuelve 502. El respaldo local vive en el frontend (ver abajo).

### `apps/inventario/views.py` — `FuncionarioViewSet`
- `GET /api/inventario/funcionarios/buscar-por-cedula/?cedula=X` — busca un Funcionario **ya conocido localmente**, sin tocar SISCOM. Es el respaldo cuando no hay red del DEM.
- `GET /api/inventario/funcionarios/{id}/perfil/` — devuelve los datos del funcionario + **todos sus bienes asignados actualmente** (código, nombre, tipo, estado, sede, área, fecha), ya resuelto en un solo array (sin duplicar la ficha de la persona).

### `apps/inventario/views.py` — `BienViewSet.inventario_general_pdf`
Ahora acepta query params (`sede`, `area`, `direccion_general`, `estado`, `tipo`, `search`) y filtra server-side antes de generar el PDF — pensado para cuando haya mucho volumen de datos, no traer todo siempre.

### Serializers
- `BienSerializer` (y Automotor/Inmueble) exponen `asignacion_activa` (con `funcionario_nombre`, `funcionario_cedula`, `area_id`, `direccion_general`, `fecha_asignacion`) y `tipo` (`MUEBLE`/`AUTOMOTOR`/`INMUEBLE`).
- `BienViewSet.queryset` tiene `select_related('automotor', 'inmueble')` para que calcular `tipo` no dispare una consulta extra por fila.

### `pdf_generator.py`
Reescrito para calcar el formato oficial del DEM (logo, grillas gris/blanco/negro como las plantillas Excel de la Dirección de Bienes Públicos) en los 5 documentos que se usan: Comprobante de Reasignación, Ficha de Mantenimiento, Inventario General, Relación de Desincorporación, Control de Incorporaciones.

**Campos que el formato oficial pide pero el sistema todavía no captura** (quedan en blanco en el PDF): condición física del bien, RIF del proveedor, control perceptil, cantidad y N° de nota de entrega/factura en incorporaciones, y las 2 preguntas de disponibilidad presupuestaria en mantenimiento.

---

## Cambios de fondo (frontend)

### Nueva página: Perfil de Funcionario
`/asignaciones/perfil` (enlace en el menú lateral, y desde el nombre del funcionario en la lista de Asignaciones).
- Busca por cédula: intenta SISCOM, si falla cae automáticamente al directorio local.
- Muestra **una tarjeta del funcionario + una tabla con todos sus bienes asignados**, sin repetir la ficha de la persona por cada bien.

### Nueva Asignación
- Ahora también tiene el respaldo local (SISCOM → si falla → `Funcionario` local) — antes se bloqueaba por completo si no había red del DEM.
- Envía `funcionario` en vez de `usuario` al crear la asignación.

### Reportes SUDEBIN
- Filtros nuevos en el "Generador Interactivo": Tipo de Bien, Dirección General, Área/Oficina (con cascada), además de Sede/Estado/Búsqueda que ya existían.
- El botón "Descargar Reporte (N)" ahora descarga **lo que está filtrado en pantalla**, no siempre el inventario completo.
- Restyle completo a los componentes Phoenix del resto de la app (antes tenía CSS propio).

### Órdenes de Compra
- El documento adjunto es obligatorio (con aviso claro en el modal: *"esta sección es solo para cargar una orden ya emitida... no para crearla"*).

### Otras pantallas ajustadas por el cambio `usuario` → `funcionario`
`lista-asignaciones`, `lista-bienes`, `lista-automotores`, `lista-inmuebles`, `sudebin-reportes` (selector de reasignación).

---

## Modelo de datos actual (resumen)

```
Sede
 └─ Area (codigo, direccion_general, activa)
     └─ Funcionario (cedula, nombres, apellidos, cargo)  ← sin login
Bien (+ Automotor / Inmueble vía herencia multi-tabla)
 └─ Asignacion (bien, funcionario, area, activa)
 └─ TrazabilidadMovimientos (histórico de incorporación/reasignación/desincorporación)
 └─ MantenimientoBien
OrdenCompra (archivo_documento obligatorio)
CustomUser (login, roles ADMINISTRADOR/OPERADOR/AUDITOR) ← NO es Funcionario
```

---

## Estado actual de los datos de prueba

Se corrió `reset_datos_prueba` para dejar la base limpia, y luego se cargó **manualmente por la interfaz** (para prueba de flujo):
- 5 bienes: 2 muebles, 2 automotores, 1 inmueble.
- 3 funcionarios: `V-31071910` (Diego Figueroa, dato real), `V-30654599` y `V-30887023` (marcados explícitamente como **"FUNCIONARIO DE PRUEBA"** — no son nombres reales, se crearon así porque este entorno no tiene acceso a SISCOM).
- 4 asignaciones activas (Diego Figueroa tiene 2 bienes, para probar el perfil agrupado).

**Antes de usar esto en serio, conviene:**
- Correr `python manage.py reset_datos_prueba --yes` de nuevo para partir en limpio, o
- Editar/borrar manualmente los 2 `Funcionario` de prueba una vez tengas los datos reales de esas cédulas vía SISCOM (la próxima consulta por esa cédula los va a sobreescribir automáticamente con los datos reales).

---

## Pendientes / Notas para continuar

- [ ] **No existe pantalla para crear un Funcionario manualmente.** Si SISCOM no encuentra a alguien (o no hay red) y tampoco está en el directorio local, hoy no hay forma de darlo de alta desde la interfaz. Se resolvió por script en las pruebas — falta la UI.
- [ ] **Excel grande de bienes** (el que mencionaste que "es demasiada data") — quedó en pausa, sin definir la estrategia de importación masiva.
- [ ] `tests.py` de `inventario` sigue roto/desactualizado (referencia modelos que ya no existen) — hay que reescribirlo contra el esquema actual con `Funcionario`.
- [ ] Los endpoints masivos (`reasignar-masivo`, `desincorporar-masivo`, `mantenimiento-masivo`) devuelven el PDF directo; evaluar si conviene devolver también un JSON con el resumen.
- [ ] Campos del formato oficial de PDF que faltan capturar (ver sección de `pdf_generator.py` arriba).
- [ ] Quedan 6 áreas "genéricas" viejas si en algún momento se restaura un dump anterior al de esta sesión — ya no deberían existir en la base actual, pero si aparecen, hay que volver a correr la reconciliación (reasignar y borrar).

---

## Estado técnico

```
Backend:  Django 5.2 + DRF + PostgreSQL
Frontend: Angular 19 (standalone components) + Phoenix/Bootstrap 5
PDFs:     ReportLab — calco del formato oficial DEM
Auth:     JWT (simplejwt) — solo para CustomUser (staff de Bienes Públicos)
RRHH:     SISCOM (wssiscom.dem.int) — solo accesible en red del DEM
Excel:    pandas + openpyxl (.xlsx) + xlrd (.xls) — agregados a requirements.txt
```
