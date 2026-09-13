# Instalación y configuración del Backend

## Descripción general

Este documento explica los pasos necesarios para configurar y ejecutar
el backend de SignIA en un entorno local.

El backend está desarrollado utilizando FastAPI con Python y utiliza
PostgreSQL como sistema de persistencia. Además, integra módulos
adicionales para autenticación, recuperación de contraseña y
procesamiento mediante visión computacional.

------------------------------------------------------------------------

# Requisitos previos

Antes de iniciar la configuración del proyecto es necesario contar con:

-   Git.
-   Python 3.12.
-   PostgreSQL.
-   pip o uv como gestor de dependencias.

Se recomienda utilizar un entorno virtual para evitar conflictos entre
dependencias.

------------------------------------------------------------------------

# Configuración del entorno virtual

## Usando uv

Crear entorno virtual:

    uv venv

Activar entorno virtual:

Windows:

    .venv\Scripts\activate

Linux:

    source .venv/bin/activate

------------------------------------------------------------------------

# Instalación de dependencias

Las dependencias se encuentran en:

-   requirements.txt
-   requirements-recuperacion.txt
-   requirements.lock.txt

Instalación usando uv:

    uv pip install -r requirements.txt

Instalación usando pip:

    pip install -r requirements.txt

Para instalar versiones exactas:

    pip install -r requirements.lock.txt

------------------------------------------------------------------------

# Configuración de variables de entorno

Crear un archivo `.env` en la raíz del proyecto.

Ejemplo:

    DATABASE_URL=

    JWT_SECRET=

    JWT_EXPIRE_MINUTES=60

    SMTP_HOST=
    SMTP_PORT=587
    SMTP_SECURITY=starttls
    SMTP_USER=
    SMTP_PASSWORD=
    SMTP_FROM=

    RECUPERACION_URL=

    MICROSOFT_CLIENT_ID=

    CORREO_TRANSPORTE=graph

------------------------------------------------------------------------

# Descripción de variables

  Variable              Descripción
  --------------------- -------------------------------------
  DATABASE_URL          Conexión con PostgreSQL
  JWT_SECRET            Clave para generación de tokens JWT
  JWT_EXPIRE_MINUTES    Tiempo de expiración del token
  SMTP_HOST             Servidor de correo
  SMTP_PORT             Puerto SMTP
  SMTP_SECURITY         Seguridad del correo
  SMTP_USER             Usuario del servicio SMTP
  SMTP_PASSWORD         Contraseña del servicio SMTP
  SMTP_FROM             Correo remitente
  RECUPERACION_URL      URL del proceso de recuperación
  MICROSOFT_CLIENT_ID   Identificador de Microsoft Graph
  CORREO_TRANSPORTE     Método de envío de correos

------------------------------------------------------------------------

# Configuración de base de datos

El backend utiliza PostgreSQL.

La conexión se realiza mediante:

    DATABASE_URL=

Los archivos iniciales de base de datos se encuentran en:

    database/
    ├── schema.sql
    ├── seed.sql
    └── README.md

Estos archivos contienen la estructura inicial y datos de prueba.

------------------------------------------------------------------------

# Ejecución del backend

Desde la raíz del proyecto ejecutar:

    uvicorn app.main:app --reload

La API estará disponible en:

    http://127.0.0.1:8000

La documentación automática de FastAPI estará disponible en:

    http://127.0.0.1:8000/docs

------------------------------------------------------------------------

# Verificación de funcionamiento

Después de iniciar el backend verificar:

1.  Que el servidor inicie correctamente.
2.  Que exista conexión con PostgreSQL.
3.  Que los endpoints funcionen desde Swagger.
4.  Que las variables de entorno estén configuradas.
5.  Que los módulos de autenticación, recuperación y visión funcionen
    correctamente.

------------------------------------------------------------------------

# Solución de problemas comunes

## ModuleNotFoundError

Indica que falta una dependencia.

Ejecutar:

    pip install -r requirements.txt

o:

    uv pip install -r requirements.txt

------------------------------------------------------------------------

## Error de conexión con PostgreSQL

Verificar:

-   DATABASE_URL.
-   Estado del servidor PostgreSQL.
-   Credenciales de acceso.

------------------------------------------------------------------------

## Error en recuperación de contraseña

Verificar:

-   SMTP_HOST.
-   SMTP_PORT.
-   SMTP_USER.
-   SMTP_PASSWORD.
-   MICROSOFT_CLIENT_ID.
-   CORREO_TRANSPORTE.

------------------------------------------------------------------------

## Error con módulo de visión

Verificar que estén instaladas:

-   OpenCV.
-   MediaPipe.

------------------------------------------------------------------------

# Tecnologías principales

-   Python 3.12.
-   FastAPI.
-   PostgreSQL.
-   Psycopg.
-   JWT.
-   OpenCV.
-   MediaPipe.
-   Microsoft Graph.
