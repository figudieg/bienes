postgre
nombre de usuario de la BD: postgres
clave:123456

----
 python manage.py createsuperuser
1. Perfil Administrador (Acceso Total)
Usuario: admin
Contraseña: Password123!
Rol: ADMINISTRADOR (Permisos totales: Gestión, Bandeja de Revisión, Historial)

2. Perfil Revisor (Especialistas)
Usuario: revisor
Contraseña: Password123!
Rol: REVISOR (Bandejas de especialistas, devoluciones y operaciones básicas)

3. Perfil Operador (Usuario estándar)
Usuario: operador
Contraseña: Password123!
Rol: OPERADOR (Módulo exclusivo de operaciones básicas de inventario y búsquedas)

----
josma
clave:admin0123456789

---------
para entrar en las carpetas 
cd /c/Users/USER/Desktop/sistemas
---

paja ejecutar el servidor de django 
python manage.py runserver 0.0.0.0:8000

Borrar el entorno actual de django
rm -r venv
Crear el nuevo entorno
python -m venv venv
Activar el nuevo entorno
.\venv\Scripts\activate
Reinstalar las librerías
pip install django djangorestframework django-cors-headers djangorestframework-simplejwt
----
paja ejecutar el servidor de angular 
ng serve -o

ejecutar para angular 
ng serve --host 0.0.0.0

----------esto es para antigravity
# Reestructuración e Integración Full-Stack de SUDEVIP

Este plan detalla la intervención profunda en el proyecto "Sistema de Bienes Públicos (SUDEVIP)", enfocándose en la integración limpia entre el frontend (Angular) y el backend (Django REST Framework), manteniendo intacta la estética actual.

## > [!IMPORTANT]
## User Review Required
- **Validación de Roles:** Se actualizarán los roles del frontend para que coincidan exactamente con el backend: `ADMINISTRADOR`, `REVISOR` y `OPERADOR`.
- **Rutas y Permisos:** El rol `OPERADOR` tendrá su acceso restringido únicamente al módulo de operaciones, bloqueando explícitamente vistas de administración y reportes globales.

## > [!WARNING]
## Open Questions
- **Generación de Reportes PDF:** ¿Existe ya un endpoint específico en el backend (ej. `/api/inventario/reportes/pdf/`) para la descarga de PDFs, o será necesario implementar uno nuevo/identificar el actual?
- **Rutas de Angular Actuales:** Actualmente existen los módulos "operaciones", "admin" y "especialistas". ¿El módulo "especialistas" se renombrará a algo como "reportes" / "revision", o mantenemos la estructura de carpetas pero solo cambiamos quién puede acceder?

---

## Proposed Changes

### Frontend Global Cleanup (Purga de 'fasdem')

Se eliminará toda mención y lógica heredada del proyecto anterior ('fasdem'), asegurando que no afecte el CSS/SCSS existente.

#### [MODIFY] package.json
- Renombrar el proyecto de `proyecto-fasdem` a `sudevip-frontend`.

#### [MODIFY] angular.json
- Limpiar referencias a `fasdem` si las hay en la configuración de build.

---

### Integración Backend-Frontend (Auth y API)

Se conectará Angular con los endpoints de Django REST Framework, implementando seguridad mediante JWT.

#### [MODIFY] src/app/app.config.ts
- Inyectar el `HttpClient` de Angular y configurar los interceptores de Auth y Error globalmente.

#### [MODIFY] src/app/core/services/auth.service.ts
- Eliminar los usuarios 'mockeados'.
- Implementar peticiones reales HTTP a `POST /api/users/auth/login/` para obtener los tokens JWT.
- Almacenar el token de acceso de forma segura para las siguientes peticiones.

#### [MODIFY] src/app/core/interceptors/auth-interceptor.ts
- Configurar el interceptor para adjuntar el token (`Bearer <token>`) en las cabeceras `Authorization` de todas las llamadas a la API (ej. `/api/inventario/...`).

#### [MODIFY] src/app/core/interceptors/error-interceptor.ts
- Capturar errores `401 Unauthorized` o fallos de red para mostrar notificaciones amigables (usando SweetAlert2 o el sistema de notificaciones actual).

#### [MODIFY] src/app/features/auth/pages/login.ts
- Actualizar la lógica del componente para manejar los estados de carga y mostrar errores devueltos por el backend (ej. "Credenciales incorrectas" o "Error de conexión").

---

### Lógica de Roles y Permisología (Control de Acceso)

Mapear los roles del `CustomUser` de Django para proteger las rutas en Angular.

#### [MODIFY] src/app/core/guards/role.guard.ts
- Actualizar la validación para verificar contra los roles: `ADMINISTRADOR`, `REVISOR`, `OPERADOR`.

#### [MODIFY] src/app/app.routes.ts
- Cambiar los permisos de las rutas:
  - `operaciones`: Accesible por `OPERADOR`, `REVISOR`, `ADMINISTRADOR`.
  - `admin`: Accesible solo por `ADMINISTRADOR`.
  - `especialistas` (o su equivalente para reportes/revisión): Accesible por `REVISOR` y `ADMINISTRADOR`.

#### [MODIFY] src/app/shared/components/sidebar/sidebar.ts (y sidebar.html)
- Añadir directivas o condicionales (`*ngIf`) para mostrar/ocultar los botones del menú lateral dinámicamente según el rol del usuario autenticado, asegurando que el `OPERADOR` vea una versión reducida.

#### [MODIFY] Mapeo de Servicios de Inventario
- Actualizar/Crear servicios en Angular para apuntar a:
  - `GET /api/inventario/bienes/` (Listar bienes)
  - `POST /api/inventario/bienes/` (Registrar bienes)
  - Endpoints de Reportes y Trazabilidad de Auditoría (`/api/auditoria/logs/`).

---

## Verification Plan

### Automated Tests
- Validar mediante el CLI de Angular que la aplicación compila correctamente (`ng build`).

### Manual Verification
1. **Flujo de Login:** Probar el inicio de sesión con credenciales válidas y verificar que el token JWT se guarde y se envíe en las cabeceras.
2. **Validación de Roles:** Iniciar sesión con un usuario `OPERADOR` y verificar que **NO** se muestran opciones de administración en el menú y que acceder a `/admin` por URL redireccione o muestre un error.
3. **Flujo de Navegación:** Comprobar la redirección de Login -> Dashboard y el funcionamiento del Logout.
4. **Manejo de Errores:** Apagar temporalmente el servidor de Django e intentar hacer login para confirmar que la UI responde con un mensaje amigable.
5. **Estética:** Asegurar que los colores, botones, y gráficas en los diferentes paneles no han sufrido alteraciones.
