# Arquitectura del Backend

## Descripción general

El backend de SignIA está desarrollado utilizando una arquitectura basada en capas, donde se separan las responsabilidades de rutas, lógica de negocio, validación de datos, seguridad, persistencia y procesamiento visual.

La comunicación general del sistema sigue el flujo:
Cliente -> Routes -> Services -> Base de datos / Módulo de visión -> Respuesta HTTP

Esta separación permite mantener el código organizado y facilitar la incorporación de nuevas funcionalidades.

------------------------------------------------------------------------

# Estructura del backend

``` text
app/
├── main.py
├── security.py
├── routes/
├── services/
└── vision/

conf/
└── database.py

src/
└── schemas/

database/
├── schema.sql
├── seed.sql
└── README.md
```

------------------------------------------------------------------------

# Componentes principales

## app/

Contiene la implementación principal del backend y la lógica necesaria
para el funcionamiento de la API.

## main.py

Archivo principal de ejecución del backend.

Responsabilidades:

-   Crear la aplicación FastAPI.
-   Registrar las rutas disponibles.
-   Configurar elementos generales del sistema.

------------------------------------------------------------------------

# Routes

Ubicación:

app/routes/

Contiene los endpoints disponibles para la comunicación con el cliente.

Las rutas reciben solicitudes HTTP, validan la información recibida y
delegan el procesamiento a los servicios correspondientes.

## autenticacion.py

Gestiona los procesos relacionados con autenticación:

-   Registro de usuarios.
-   Inicio de sesión.
-   Generación de tokens.

## usuarios.py

Contiene operaciones relacionadas con la gestión de usuarios.

## letras.py

Gestiona el módulo del alfabeto LSC:

-   Consulta de letras registradas.
-   Consulta de información específica.
-   Actualización de información.

## perfil.py

Gestiona la información del perfil del usuario y su progreso.

## recuperacion_contrasena.py

Controla la solicitud de recuperación de contraseña.

## restablecimiento_contrasena.py

Permite establecer una nueva contraseña después de validar la solicitud
de recuperación.

------------------------------------------------------------------------

# Services

Ubicación:

app/services/

Contiene la lógica de negocio del sistema.

Las rutas utilizan estos servicios para realizar operaciones y evitar
incluir lógica directamente dentro de los endpoints.

## autenticacion_service.py

Implementa la lógica relacionada con autenticación y validación de
usuarios.

## usuarios_service.py

Contiene operaciones relacionadas con usuarios y persistencia.

## letras_service.py

Gestiona la consulta y actualización de información del alfabeto LSC.

## perfil_service.py

Gestiona la información del perfil y progreso del usuario.

## recuperacion_service.py

Maneja la creación de solicitudes de recuperación de contraseña.

## restablecimiento_service.py

Realiza la actualización de contraseña después de validar el token de
recuperación.

## correo_recuperacion_service.py

Gestiona el envío de correos utilizados en el proceso de recuperación.

## microsoft_oauth_service.py

Gestiona la autenticación requerida para utilizar Microsoft Graph.

## vision_service.py

Permite utilizar el módulo de computación visual desde la arquitectura
del backend.

Este servicio actúa como intermediario entre la API y el módulo de
visión.

------------------------------------------------------------------------

# Módulo de visión

Ubicación:

app/vision/

Contiene la lógica relacionada con procesamiento y reconocimiento
mediante visión computacional.

## detector.py

Gestiona la detección de manos utilizando MediaPipe.

## reconocimiento.py

Contiene la lógica encargada del reconocimiento visual.

## vocales.py

Implementa las reglas utilizadas para identificar posiciones
correspondientes a vocales en Lengua de Señas Colombiana.

## models/

Contiene los modelos utilizados por MediaPipe.

Actualmente contiene:

hand_landmarker.task

## prototype/

Contiene el prototipo inicial de ejecución mediante cámara.

------------------------------------------------------------------------

# Schemas

Ubicación:

src/schemas/

Contiene los modelos de validación utilizados por la API mediante
Pydantic.

Responsabilidades:

-   Definir estructuras de entrada.
-   Validar datos recibidos.
-   Definir estructuras de respuesta.

------------------------------------------------------------------------

# Configuración

Ubicación:

conf/

Contiene archivos relacionados con configuración del backend.

Actualmente incluye:

database.py

Este archivo administra la conexión con la base de datos PostgreSQL.

------------------------------------------------------------------------

# Base de datos

Ubicación:

database/

Contiene archivos relacionados con la estructura inicial de la base de
datos.

Incluye:

-   Definición de tablas.
-   Datos iniciales.
-   Documentación del esquema.

------------------------------------------------------------------------

# Seguridad

Archivo:

app/security.py

Contiene funcionalidades relacionadas con seguridad del sistema:

-   Creación de tokens JWT.
-   Validación de usuarios autenticados.
-   Control de permisos administrativos.
