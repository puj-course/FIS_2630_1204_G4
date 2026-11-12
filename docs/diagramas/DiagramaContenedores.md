# Diagrama de contenedores (C4 nivel 2) — SignIA

## Propósito

Este diagrama muestra los contenedores que forman SignIA (las piezas que se ejecutan o almacenan datos por separado), la persona que los usa, el sistema externo con el que se comunican y la tecnología de cada relación.

## Diagrama

<img width="952" height="734" alt="Untitled" src="https://github.com/user-attachments/assets/8054d725-988e-4585-b4e7-74daae09be3b" />


## Elementos

| Elemento | Tipo C4 | Tecnología | Responsabilidad |
|---|---|---|---|
| Usuario | Persona | — | Aprende el alfabeto de la Lengua de Señas Colombiana, practica y consulta su progreso. |
| Aplicación web | Contenedor | React y TypeScript | Interfaz para aprender, practicar señas con reconocimiento en tiempo real y consultar el progreso. |
| API SignIA | Contenedor | Python y FastAPI | Gestiona autenticación (JWT), letras, práctica, progreso, historial y usuarios, y reconoce las señas a partir de los fotogramas recibidos. |
| Base de datos | Contenedor | PostgreSQL (Neon) | Almacena la información persistente del sistema. |
| Microsoft Graph y plataforma de identidad | Sistema externo | — | Emite el token OAuth de la cuenta remitente y envía el correo de recuperación de contraseña. |

## Relaciones

| Origen → Destino | Descripción | Tecnología |
|---|---|---|
| Usuario → Aplicación web | Practica señas y consulta su progreso. | — |
| Aplicación web → API SignIA | Envía fotogramas, credenciales y datos de práctica. | REST/JSON, JWT |
| API SignIA → Base de datos | Lee y escribe datos. | SQL, psycopg |
| API SignIA → Microsoft | Obtiene un token y envía el correo de recuperación. | HTTPS/JSON, OAuth 2.0 |
| Microsoft → Usuario | Envía el correo de recuperación. | — |

## Evidencia en el código

| Afirmación del diagrama | Fuente |
|---|---|
| El frontend en uso es React con TypeScript. | `src/front/srcFront/` |
| La API está construida con FastAPI y tiene un único punto de entrada. | `app/main.py` |
| La API y el frontend son contenedores separados; la API solo sirve archivos de `app/assets`. | `app/main.py` (`StaticFiles` y `CORSMiddleware`) |
| El frontend envía fotogramas en base64 a la API. | `src/front/srcFront/services/vision.ts` (`POST /vision/reconocer`) |
| La autenticación usa tokens JWT de tipo Bearer. | Módulo de autenticación de la API (`HTTPBearer`, `jwt.encode` / `jwt.decode`) |
| El reconocimiento de señas se ejecuta dentro de la API. | `app/services/vision_service.py` importa `app.vision`; `app/main.py` registra `vision_router` |
| La base de datos es PostgreSQL. | `conf/database.py` (`psycopg.connect`) |
| La recuperación de contraseña por correo está activa. | `app/routes/autenticacion.py` incluye `router_recuperacion` |
| El correo se envía mediante Microsoft Graph con un token OAuth obtenido con MSAL. | `app/services/correo_recuperacion_service.py` y `app/services/microsoft_oauth_service.py` |

## Alcance y omisiones

- No se representan el navegador ni la cámara web: forman parte del entorno del usuario, no son contenedores de SignIA.
- El reconocimiento de señas (`app/vision`) no aparece como contenedor porque se ejecuta en el mismo proceso que la API. Se detallará en el diagrama de componentes del backend.
- No se representan el script de autorización inicial de la cuenta de Microsoft (se ejecuta una sola vez durante la configuración) ni la caché cifrada local del token.
- No se representan la carpeta `web/`, que no está en uso, ni el prototipo de `app/vision/prototype`.
- La identidad de Microsoft y Microsoft Graph se agrupan en un solo sistema externo porque, para SignIA, cumplen una única función: enviar el correo de recuperación.
- La descripción de la base de datos en la imagen del diagrama se basa en las funciones expuestas por la API (usuarios, letras, intentos, resultados, progreso, sesiones y tokens revocados).
