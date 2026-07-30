# SUDEVIP - Sistema de Gestión de Bienes Públicos

Este es un sistema Full-Stack profesional para la administración de bienes públicos en entidades gubernamentales, desarrollado bajo los principios de Clean Architecture y la estandarización **Golden Standard**.

---

## 🏛️ Arquitectura del Proyecto (Golden Standard)

La estructura del repositorio se divide de manera estricta y segregada para garantizar la escalabilidad y el mantenimiento continuo:

```plaintext
/sistemas (Proyecto Raíz)
├── /docs                  # Documentación técnica, manuales y diagramas
│   └── guia-desarrollo.md # Guía original con roles, contraseñas y flujos
├── /scripts               # Respaldos de base de datos y migraciones
│   └── dump-bienes_publicos-202604052248.sql
├── /backend               # Servidor REST en Django (Python)
│   ├── /config            # Configuraciones del framework (settings, urls, etc.)
│   ├── /apps              # Módulos del negocio (users, inventario, auditoria)
│   ├── /core              # Lógica transversal (helpers como bcv_service, validadores)
│   ├── manage.py          # CLI de Django
│   └── requirements.txt   # Librerías de Python
├── /frontend              # Aplicación Cliente en Angular (TypeScript)
│   ├── /src
│   │   ├── /app
│   │   │   ├── /core      # Servicios base, interceptores, guards
│   │   │   ├── /shared    # Componentes comunes, pipes y directivas
│   │   │   ├── /features  # Módulos de negocio (bienes, ordenes, auditoria)
│   │   │   └── /pages     # Vistas de nivel superior (e.g. PageNotFound)
│   │   └── /assets        # Recursos estáticos (imágenes, iconos)
│   ├── angular.json
│   └── package.json
├── .gitignore             # Exclusiones globales de control de versiones
├── .env.example           # Plantilla de variables de entorno global
└── README.md              # Esta guía rápida
```

---

## 🚀 Requisitos e Instalación Rápida

### 1. Variables de Entorno
Copia la plantilla `.env.example` en la raíz del proyecto para crear tu archivo de configuración:
```bash
cp .env.example .env
```
Ajusta las credenciales de PostgreSQL y la clave de Django en el archivo `.env`.

---

### 2. Configuración del Backend (Django REST Framework)

1. Dirígete a la carpeta `/backend`:
   ```bash
   cd backend
   ```
2. Crea e inicia un entorno virtual de Python:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Instala todas las dependencias requeridas:
   ```bash
   pip install -r requirements.txt
   ```
4. Ejecuta las migraciones de base de datos:
   ```bash
   python manage.py migrate
   ```
5. **Carga los datos iniciales y usuarios de prueba:**
   ```bash
   python manage.py seed_users
   ```
6. Corre el servidor de desarrollo local:
   ```bash
   python manage.py runserver
   ```
   El backend estará disponible en: [http://localhost:8000](http://localhost:8000)

---

### 3. Configuración del Frontend (Angular)

1. Dirígete a la carpeta `/frontend`:
   ```bash
   cd frontend
   ```
2. Instala los paquetes de Node.js:
   ```bash
   npm install
   ```
3. Inicia el servidor de desarrollo de Angular:
   ```bash
   ng serve -o
   ```
   La aplicación se abrirá automáticamente en: [http://localhost:4200](http://localhost:4200)

---

## 🔐 Usuarios y Roles de Prueba (Seeding)

Tras ejecutar `python manage.py seed_users`, contarás con los siguientes perfiles de prueba en tu base de datos:

| Rol | Usuario | Contraseña | Permisos |
| :--- | :--- | :--- | :--- |
| **ADMINISTRADOR** | `admin` | `Password123!` | Acceso completo a administración, bandeja de revisión e historial. |
| **AUDITOR** | `auditor` | `Password123!` | Acceso a bandeja de especialistas, devoluciones e historial. |
| **OPERADOR** | `operador` | `Password123!` | Acceso exclusivo a operaciones básicas de inventario y búsquedas. |
