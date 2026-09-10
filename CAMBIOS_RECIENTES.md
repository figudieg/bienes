# Estado del Proyecto — Sistema de Bienes Públicos DEM

> **Última actualización:** 10 Sep 2026

---

## Resumen ejecutivo

### 10 Sep — autocompletar con SISCOM en Gestión de Usuarios + commit de todo lo pendiente

1. **Nuevo Usuario / Editar Usuario ahora se llena desde SISCOM** — botón de búsqueda junto a Cédula (también dispara con Enter) que autocompleta Usuario, Nombre, Apellido, Cargo y Área. Los 5 campos quedan **bloqueados** por defecto (solo se editan a través de la búsqueda); si SISCOM no responde, se desbloquean automáticamente como respaldo para no dejar trabado el alta de un usuario nuevo.
2. **Username generado automáticamente**: `apellido(primeras 4 letras) + nombre(primeras 4 letras)` en minúsculas y sin tildes (nombres/apellidos más cortos usan las letras que haya). Si el resultado ya existe, agrega un sufijo numérico.
3. Se agregó `nombres`/`apellidos` (ya separados) a la respuesta de `consultar-cedula` para reutilizarla sin duplicar la lógica de separar el nombre completo.
4. Se eliminó `scripts/deploy/diagnostico_servidor.sh` (no se llegó a necesitar).
5. QA express de todo lo acumulado desde el último commit (renombrado SUDEVIP/SUDEBIN → Bienes Públicos, reestructuración de `.env`, correcciones de Calidad, numpy/requirements.txt) — probado en vivo: login, Registro de Bienes con filtros de Tipo/Categoría, Reportes de Bienes Públicos, y el flujo completo de Gestión de Usuarios (crear, validar, eliminar). Sin errores de consola ni del servidor.

### 07 Sep — correcciones de la certificación de Calidad (fase pre-producción)

El equipo de Calidad certificó el sistema en `calidad-pruebas.dem.int` y reportó 3 incidencias + 3 observaciones, todas en **Gestión de Usuarios**. Las 6 ya están resueltas:

1. **INC-001 / INC-002 — "Error al registrar/editar usuario, sin explicar el motivo".** La causa real: el backend ya rechazaba nombres/apellidos con números (`validate_first_name`/`validate_last_name` existían desde antes), pero el frontend solo sabía mostrar el mensaje de error si venía en los campos `username`, `cedula` o `password` — cualquier otro campo caía en un mensaje genérico. Se corrigió el manejo de errores en `gestion-usuarios.ts` (`extraerMensajeError()`) para mostrar el mensaje real que ya devuelve el backend, sea cual sea el campo. También se agregó validación visual inmediata (sin ir al servidor) en Nombre, Apellido y Cargo.
2. **`Cargo` sin validar** — no tenía equivalente a `validate_first_name`. Se agregó `validate_cargo` en el backend (mismo patrón que ya se usaba en `reparado_por`/`marca`/`color` en otros módulos) y su respectivo `pattern` en el frontend.
3. **INC-003 — "Editar usuario exige contraseña aunque dice 'dejar vacío para no cambiar'".** El serializer no tenía `required=False` en `password`, así que cualquier edición sin tocar la clave fallaba. Se corrigió: la contraseña ahora solo es obligatoria al **crear**; en edición, si se deja vacía, se mantiene la actual (verificado: se pudo editar un usuario sin contraseña y el login con la clave original siguió funcionando). De paso, `updateUser()` pasó de `PUT` a `PATCH` (edición parcial real).
4. **Observación: "Cargo" debería ser lista desplegable.** No existe un catálogo oficial de cargos en el sistema (es texto libre desde siempre, alimentado por SISCOM en `Funcionario` y a mano en `CustomUser`), así que en vez de inventar una lista cerrada que podría bloquear cargos reales válidos, se implementó como campo de texto **con sugerencias** (`<datalist>`) tomadas de los cargos ya usados en el sistema — sigue validado por el patrón de letras/signos comunes. **Si Calidad insiste en una lista cerrada de verdad, avisar para definir el catálogo oficial de cargos con el departamento y cambiarlo a `<select>`.**
5. **Observación: Área de Adscripción sin orden alfabético** — corregido a nivel de backend (`AreaViewSet` ahora ordena por `nombre`, antes por `id`), así que también mejora en cualquier otro selector de Área del sistema, no solo en este formulario.
6. **Observación: falta indicar el formato de contraseña esperado** — antes no había ninguna política de contraseña real (`AUTH_PASSWORD_VALIDATORS` no estaba configurado y nunca se llamaba `validate_password`, así que cualquier contraseña de 1 carácter era válida). Se agregó una política real (mínimo 8 caracteres, con letras y números) validada en backend y frontend, con el texto de ayuda correspondiente en el formulario.
7. **Extra (idea del usuario, no pedida por Calidad pero ataca la misma causa raíz):** en "Nuevo/Editar Usuario" ahora hay un botón de búsqueda junto a Cédula que consulta SISCOM (la misma integración que ya usan Nueva Asignación y Perfil de Funcionario) y autocompleta Usuario, Nombre, Apellido, Cargo y Área. Se agregó `nombres`/`apellidos` (ya separados) a la respuesta de `consultar-cedula` para poder reutilizarla aquí sin duplicar la lógica de separar el nombre completo.
   - **Username automático:** `apellido(primeras 4 letras) + nombre(primeras 4 letras)` en minúsculas y sin tildes (si el nombre/apellido tiene menos de 4 letras, usa las que haya — ej. "Ana" + "Uy" → `anauy`). Si el resultado ya existe, agrega un sufijo numérico (`valemari`, `valemari2`, `valemari3`...).
   - **Campos bloqueados por defecto** (Usuario, Nombre, Apellido, Cargo, Área): solo se llenan/editan a través del botón de búsqueda, para eliminar el error de tipeo en el origen. **Excepción de seguridad:** si SISCOM no responde (sin red del DEM, o cédula no encontrada), los campos se desbloquean automáticamente para no dejar trabado el alta de un usuario nuevo — verificado en vivo (con SISCOM inalcanzable se desbloquean solos y muestran el motivo). Rol, Estado, Email y Contraseña siguen siendo decisión manual de Bienes Públicos, no vienen de SISCOM.

### 26 Ago — preparación para desplegar en el servidor de calidad

1. **El frontend ahora tiene su propio `.env`**, igual que el backend (antes no lo tenía y había que editar `environment.ts` a mano cada vez que cambiabas de máquina — mala práctica, y la causa de un bug real: compilar para el servidor de calidad podía terminar apuntando por error a la laptop de desarrollo). Ver detalle en la sección "Cómo levantar el proyecto".
2. **Se eliminó `environment.development.ts`** — nunca estuvo conectado en `angular.json` (no había `fileReplacements` configurado), así que no hacía nada; todo el tiempo se estaba usando `environment.ts` sin importar el modo. Confirmado y limpiado.
3. **Diagnóstico de por qué el proyecto no está listo para producción tal cual está** — ver sección "Antes de desplegar en el servidor de calidad" más abajo. Nada del modelo de datos ni la lógica de negocio cambia, es pura configuración de despliegue (`DEBUG`, `SECRET_KEY`, servir con Gunicorn/Nginx en vez de `runserver`/`ng serve`, etc.).
4. ~~Script de diagnóstico del servidor~~ — se armó y luego se eliminó (10 Sep) por no ser necesario; la guía de despliegue (Gunicorn + Nginx + systemd) se arma directo cuando se tenga acceso al servidor.
5. **`.env` ahora vive dentro de `backend/`** (antes estaba en la raíz del repo, inconsistente con `frontend/.env`) — se movió el archivo y se actualizó `load_dotenv()` en `settings.py` para leerlo de ahí. `backend/.env.example` (la plantilla) se movió junto con él.
6. **`backend/.env` ya tiene los datos reales del servidor de calidad** — aplicación y base de datos en `172.26.97.36`, backend pensado para escuchar en el puerto **9005** (no el 8000 de desarrollo). El `.env` no se sube a git (por eso este resumen no repite las credenciales); si necesitas los valores exactos, están en `backend/.env` local. `frontend/.env` (`API_URL`) ya apunta a `http://172.26.97.36:9005/api`.
   - Ojo: desde esta laptop esa IP no es alcanzable (misma razón que `wssiscom.dem.int` — red/VPN), así que no pude probar la conexión real desde aquí. Falta confirmar cuando estés en la red correcta.
   - **Pendiente de confirmar:** en qué puerto va a quedar el frontend en ese mismo servidor — `CORS_ALLOWED_ORIGINS` quedó con `:4200` como suposición, hay que ajustarlo si el puerto real es otro (o si Nginx lo sirve por el 80/443 directamente).

### 21 Ago

1. **Reasignar y Desincorporar individuales.** Antes solo existían las versiones masivas (por checkboxes, en Reportes de Bienes Públicos). Ahora cada bien tiene sus propios botones de "Reasignar" y "Desincorporar" en Registro de Bienes, Automotores, Inmuebles, Asignaciones y Perfil de Funcionario — con un modal compartido que genera el mismo comprobante oficial en PDF que las versiones masivas.
2. **Lógica del "funcionario cedente" corregida.** El formulario de reasignación ya no pide escribir a mano quién entrega el bien: si el bien tiene una asignación activa, muestra el nombre real de quien lo tiene (dato del sistema, no texto libre); si no tiene a nadie asignado, no pregunta nada y aclara que se reasignará directamente.
3. **Categorías de bienes muebles + filtros más específicos.** Nuevo campo `categoria` en `Bien` (Computadora, Pantalla, Periférico, Mobiliario, Equipo de Oficina, Electrodoméstico, Herramienta, Otro). Registro de Bienes ahora filtra por Tipo (Mueble/Automóvil/Inmueble) y Categoría, en vez de mostrar todo mezclado en una sola tabla.
4. **Nueva Asignación ya no ofrece bienes que ya están asignados** — antes el selector mostraba cualquier bien `ACTIVO` sin importar si ya tenía dueño, lo que producía un error confuso al intentar asignarlo de nuevo.
5. Dos bugs encontrados y corregidos en revisión de pre-demo: el botón "Vista Compacta" del menú lateral no hacía nada (dependía de un script viejo que no se re-enlazaba con Angular), y el log de auditoría no registraba creaciones de Automotores/Inmuebles (por cómo Django dispara las señales en la herencia de tablas).

### Bloques de trabajo previos (20 Ago)

1. **Cambio de arquitectura: `Funcionario` reemplaza a `usuario` en Asignaciones.** Ahora las personas a quienes se les asignan bienes NO necesitan cuenta de login — son un directorio propio (`Funcionario`), separado de las cuentas del sistema (`CustomUser`, que son solo para el personal de Bienes Públicos que opera el sistema).
2. **Directorio real de oficinas del DEM cargado como `Area`** (53 oficinas reales, con código, dirección general y estado activo/cerrado), reemplazando las 6 áreas genéricas de prueba.
3. **Integración con SISCOM (wssiscom.dem.int)** para traer datos frescos del funcionario por cédula, con:
   - Auto-creación/sincronización del `Funcionario` local en cada consulta.
   - Matching automático de la oficina (texto libre de SISCOM → `Area` real).
   - Respaldo local automático cuando SISCOM no responde (fuera de la red del DEM).
4. **Nueva pantalla "Perfil de Funcionario"** que resuelve el problema de ver los bienes de una persona repetidos en la lista de asignaciones.

También se rediseñó el módulo de Reportes de Bienes Públicos (estilo + filtros), se generaron los PDFs con el formato oficial del DEM, y se ajustó Órdenes de Compra para que sea solo carga/constancia, no creación.

---

## Cómo levantar el proyecto (en una máquina nueva)

```bash
# 1. Backend
cd backend
python -m venv venv        # o el venv que ya tengas
venv\Scripts\activate
pip install -r requirements.txt   # incluye pandas/openpyxl/xlrd ahora

# 2. Variables de entorno — crear backend/.env (NO se commitea)
cp .env.example .env
# editar backend/.env y completar DB_PASSWORD, WSSISCOM_EVALUACION_URL, etc.

# 3. Base de datos (Postgres). Si es una BD nueva:
python manage.py migrate

# 4. Frontend
cd ../frontend
npm install
cp .env.example .env
# editar frontend/.env y poner el API_URL real de esta máquina (ver más abajo)
npm start
```

> **`frontend/.env`** (nuevo, sigue el mismo patrón que el `.env` del backend — antes el frontend no tenía uno y había que editar `environment.ts` a mano, lo cual era fácil de olvidar al cambiar de máquina/servidor). Define `API_URL` (a qué backend le habla el frontend) y `PRODUCTION` (true solo en el build de QA/producción). `npm start` y `npm run build` generan automáticamente `src/environments/environment.ts` a partir de este archivo (script `frontend/scripts/set-env.js`) — **no edites `environment.ts` a mano**, se sobrescribe en cada arranque/build.

> **Nota de red:** el endpoint de consulta de funcionario por cédula (`consultar-cedula`) depende de `wssiscom.dem.int`, solo accesible **dentro de la red del DEM**. Fuera de esa red vas a ver error 502 — es esperado. Para eso existe el respaldo local (ver más abajo).
> Si usas una VPN personal (ej. ProtonVPN) para otras cosas en la misma máquina donde trabajas con el DEM, puede "tapar" el acceso a la red interna. La solución no es apagar la VPN cada vez: en el cliente VPN busca la opción de **acceso a la red local / split tunneling** y excluye tu subred del DEM (en la máquina de prueba fue `172.26.96.0/21`) — así el tráfico a `wssiscom.dem.int` sigue por tu red normal y el resto de tu tráfico sigue por la VPN.

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

### `apps/inventario/models.py` — campo `categoria` en `Bien`
Nuevo campo (migración `0010_bien_categoria.py`), solo aplica en la práctica a bienes muebles: `COMPUTADORA`, `PANTALLA`, `PERIFERICO`, `MOBILIARIO`, `EQUIPO_OFICINA`, `ELECTRODOMESTICO`, `HERRAMIENTA`, `OTRO`. Opcional (`blank=True, null=True`) — los bienes cargados antes de este cambio quedan sin categoría hasta que se editen manualmente.

### `apps/inventario/views.py` — `BienViewSet.reasignar` / `.desincorporar` (individuales)
`POST /api/inventario/bienes/{id}/reasignar/` y `POST /api/inventario/bienes/{id}/desincorporar/` — mismo comportamiento que las versiones `-masivo` (desactivan la asignación anterior, crean la traza de `TrazabilidadMovimientos`, generan el comprobante PDF), pero para un solo bien y devolviendo el PDF individual en vez de forzar el formato "masivo". La lógica común se movió a los métodos privados `_reasignar_bien`/`_desincorporar_bien` para no duplicarla entre la versión individual y la masiva.

---

## Cambios de fondo (frontend)

### Nueva página: Perfil de Funcionario
`/asignaciones/perfil` (enlace en el menú lateral, y desde el nombre del funcionario en la lista de Asignaciones).
- Busca por cédula: intenta SISCOM, si falla cae automáticamente al directorio local.
- Muestra **una tarjeta del funcionario + una tabla con todos sus bienes asignados**, sin repetir la ficha de la persona por cada bien.

### Nueva Asignación
- Ahora también tiene el respaldo local (SISCOM → si falla → `Funcionario` local) — antes se bloqueaba por completo si no había red del DEM.
- Envía `funcionario` en vez de `usuario` al crear la asignación.

### Reportes de Bienes Públicos
- Filtros nuevos en el "Generador Interactivo": Tipo de Bien, Dirección General, Área/Oficina (con cascada), además de Sede/Estado/Búsqueda que ya existían.
- El botón "Descargar Reporte (N)" ahora descarga **lo que está filtrado en pantalla**, no siempre el inventario completo.
- Restyle completo a los componentes Phoenix del resto de la app (antes tenía CSS propio).

### Órdenes de Compra
- El documento adjunto es obligatorio (con aviso claro en el modal: *"esta sección es solo para cargar una orden ya emitida... no para crearla"*).

### Otras pantallas ajustadas por el cambio `usuario` → `funcionario`
`lista-asignaciones`, `lista-bienes`, `lista-automotores`, `lista-inmuebles`, `reportes-bienes-publicos` (selector de reasignación).

### Componente compartido: `shared/components/gestion-bien-modal`
Modal único para Reasignar/Desincorporar un solo bien, usado desde Registro de Bienes, Automotores, Inmuebles, Asignaciones y Perfil de Funcionario (evita repetir el mismo formulario 5 veces). Recibe el `bien` (con su `asignacion_activa` si tiene) y el `modo`:
- **Reasignar**: pide Sede/Área destino (obligatorio), Funcionario destino (opcional — se puede reasignar solo a un depósito/área sin nombrar a alguien todavía) y motivo. Si el bien ya tiene un funcionario asignado, lo muestra como dato informativo ("Funcionario cedente: ..."); si no tiene a nadie, no pide ese dato.
- **Desincorporar**: solo pide el motivo (criterio legal de Bienes Públicos).

Ambos botones se ocultan si el bien ya está `DESINCORPORADO` (no tiene sentido reasignar o desincorporar algo que ya se dio de baja).

### Registro de Bienes — filtros de Tipo y Categoría
Antes esta pantalla mostraba **todos** los bienes (incluyendo automotores e inmuebles, porque comparten la misma tabla base en la base de datos), sin forma de separarlos. Ahora tiene un filtro de Tipo (Mueble/Automóvil/Inmueble) y, dentro de Mueble, un filtro de Categoría. El botón "Editar" también se corrigió para llevar a la pantalla correcta según el tipo real del bien (antes siempre intentaba abrir el formulario de mueble genérico).

### Nueva Asignación
El selector de "Bien Activo" ahora excluye los bienes que ya tienen una asignación activa (antes solo filtraba por `estado === 'ACTIVO'`, así que ofrecía bienes que ya tenían dueño y el backend rechazaba la asignación con un error).

---

## Modelo de datos actual (resumen)

```
Sede
 └─ Area (codigo, direccion_general, activa)
     └─ Funcionario (cedula, nombres, apellidos, cargo)  ← sin login
Bien (categoria, solo relevante para muebles) (+ Automotor / Inmueble vía herencia multi-tabla)
 └─ Asignacion (bien, funcionario, area, activa)
 └─ TrazabilidadMovimientos (histórico de incorporación/reasignación/desincorporación)
 └─ MantenimientoBien
OrdenCompra (archivo_documento obligatorio)
CustomUser (login, roles ADMINISTRADOR/OPERADOR/AUDITOR) ← NO es Funcionario
```

---

## Estado actual de los datos de prueba

Los mismos 5 bienes de la sesión anterior se usaron hoy para probar en vivo Reasignar/Desincorporar (uno de los automotores terminó `DESINCORPORADO` y las asignaciones se movieron entre los funcionarios de prueba varias veces). Los datos ya no reflejan un flujo "limpio" — antes de mostrar el sistema conviene partir de cero:

```bash
python manage.py reset_datos_prueba --yes
```

Después de resetear, la base queda con usuarios/Sedes/Áreas intactos pero sin bienes/asignaciones/funcionarios, listo para cargar de nuevo por la interfaz (o con SISCOM ya funcionando, si estás en la red del DEM).

**Nota:** si vuelves a crear los funcionarios de prueba con las cédulas `V-30654599` / `V-30887023` sin acceso a SISCOM, van a quedar marcados como **"FUNCIONARIO DE PRUEBA"** (no son nombres reales) — la próxima consulta a esa cédula vía SISCOM los sobreescribe automáticamente con los datos reales.

---

## Antes de desplegar en el servidor de calidad

El proyecto hoy está configurado enteramente para desarrollo local — no para vivir en un servidor. Nada de esto toca el modelo de datos ni la lógica de negocio, es solo configuración de despliegue:

- **`DEBUG=True`** en `.env` → debe ser `False`. Con `True`, cualquier error expone el stack trace completo (variables de entorno, queries, rutas del servidor) a quien lo dispare.
- **`SECRET_KEY`** → hoy usa el valor `django-insecure-...` de ejemplo. Generar uno real para el servidor de calidad, distinto al de desarrollo.
- **`ALLOWED_HOSTS='*'`** → restringir al dominio/IP real del servidor.
- **`CORS_ALLOW_ALL_ORIGINS=True`** → pasar a `False`, con `CORS_ALLOWED_ORIGINS` apuntando solo al origen real del frontend.
- ~~`DB_PASSWORD=123`~~ → **ya resuelto**, `.env` tiene las credenciales reales del servidor de calidad (usuario `usr_bienespublicos`, base `bd_bienes_publicos` en `172.26.97.36`).
- **Backend**: `manage.py runserver` no es apto para producción (el propio Django lo advierte). Necesita **Gunicorn** detrás de **Nginx**, con un servicio `systemd` para que se reinicie solo si el proceso muere o el servidor reinicia.
- **Frontend**: `ng serve` tampoco es apto para producción (Angular lo advierte igual). Hay que compilar con `npm run build` (con `PRODUCTION=true` en `frontend/.env`) y servir esos archivos estáticos con Nginx.
- **Archivos estáticos de Django** (admin, etc.) no se sirven solos con `DEBUG=False` — hace falta correr `collectstatic` y que Nginx los sirva.
- **Correo** (recuperación de clave) hoy cae al backend de consola porque no hay `EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD` — configurar si se va a usar esa función en el servidor de calidad.
- Sin backups automáticos de la base de datos todavía.

**Siguiente paso:** armar la guía de despliegue (Gunicorn + Nginx + systemd) cuando se tenga acceso directo al servidor de calidad para confirmar qué tiene instalado.

---

## Pendientes / Notas para continuar

- [ ] **Excel grande de bienes** (el que mencionaste que "es demasiada data") — quedó en pausa, sin definir la estrategia de importación masiva.
- [ ] `tests.py` de `inventario` sigue roto/desactualizado (referencia modelos que ya no existen) — hay que reescribirlo contra el esquema actual con `Funcionario`.
- [ ] Los endpoints masivos (`reasignar-masivo`, `desincorporar-masivo`, `mantenimiento-masivo`) devuelven el PDF directo; evaluar si conviene devolver también un JSON con el resumen. (Los nuevos endpoints individuales tienen el mismo comportamiento, por consistencia.)
- [ ] Campos del formato oficial de PDF que faltan capturar (ver sección de `pdf_generator.py` arriba).
- [ ] Quedan 6 áreas "genéricas" viejas si en algún momento se restaura un dump anterior al de esta sesión — ya no deberían existir en la base actual, pero si aparecen, hay que volver a correr la reconciliación (reasignar y borrar).
- [ ] Los 5 bienes de prueba cargados hoy no tienen `categoria` asignada (el campo se agregó después de crearlos) — se puede editar manualmente o simplemente resetear y recargar.
- [ ] Sin definir todavía: si `reasignar`/`reasignar-masivo` deben seguir actualizando `bien.sede` al destino automáticamente (hoy lo hacen) — no es un problema mientras todo sea Sede Principal DEM, pero conviene revisarlo antes de sumar más sedes.
- **Decisión ya tomada (no es pendiente):** no se va a construir una pantalla para crear `Funcionario` manualmente — el directorio se alimenta solo desde SISCOM por diseño (ver sección de arquitectura arriba).

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
