# SignIA 💙

**"Aprender para comunicar, comunicar para incluir."**

[![Backend CI](https://github.com/puj-course/FIS_2630_1204_G4/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/puj-course/FIS_2630_1204_G4/actions/workflows/backend-ci.yml)

[![Frontend CI](https://github.com/puj-course/FIS_2630_1204_G4/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/puj-course/FIS_2630_1204_G4/actions/workflows/frontend-ci.yml)

[![Docker Check](https://github.com/puj-course/FIS_2630_1204_G4/actions/workflows/docker-check.yml/badge.svg)](https://github.com/puj-course/FIS_2630_1204_G4/actions/workflows/docker-check.yml)

## Descripción

SignIA es una plataforma web multiusuario orientada al aprendizaje y reconocimiento del alfabeto de la Lengua de Señas Colombiana (LSC) mediante visión por computador, la plataforma facilita la práctica del alfabeto de la LSC utilizando la cámara del dispositivo, permitiendo identificar las señas realizadas por el usuario y mostrar la letra correspondiente en tiempo real.

SignIA surge como respuesta a las barreras de comunicación existentes entre personas sordas y oyentes y a la necesidad de generar herramientas tecnológicas que permitan ampliar el conocimiento básico de la LSC, la plataforma busca promover el aprendizaje autónomo, la sensibilización frente a la comunidad sorda y el uso de la tecnología como herramienta para contribuir a una comunicación más inclusiva.

## Contenido

1. [Descripción](#descripción)
2. [Inicio rápido](#inicio-rápido)
3. [Funcionalidades del proyecto](#funcionalidades-del-proyecto)
4. [Tecnologías utilizadas](#tecnologías-utilizadas)
5. [Organización del proyecto](#organización-del-proyecto)
6. [Ejecución con Docker Compose](#ejecución-con-docker-compose)
7. [Ejecución desde imágenes de Docker Hub](#ejecución-desde-imágenes-de-docker-hub)
8. [Ejecución para desarrollo sin contenedores](#ejecución-para-desarrollo-sin-contenedores)
9. [Variables de configuración](#variables-de-configuración)
10. [Cómo usar SignIA](#cómo-usar-signia)
11. [Pruebas y calidad](#pruebas-y-calidad)
12. [Despliegue](#despliegue)
13. [Base de datos](#base-de-datos)
14. [API del backend](#api-del-backend)
15. [Patrones y organización del código](#patrones-y-organización-del-código)
16. [Documentación adicional](#documentación-adicional)
17. [Solución de problemas](#solución-de-problemas)
18. [Trabajo en equipo y contribuciones](#trabajo-en-equipo-y-contribuciones)
19. [Licencia](#licencia)

## Inicio rápido

Si solo quieres ver SignIA funcionando en tu computador, necesitas **Git** y **Docker** (con Docker Compose). Desde una terminal:

```bash

git clone https://github.com/puj-course/FIS_2630_1204_G4.git

cd FIS_2630_1204_G4

cp .env.example .env

```

Abre el archivo `.env` y completa estos valores (los demás pueden quedar vacíos por ahora):

```dotenv

POSTGRES_PASSWORD=una_contraseña_que_tú_elijas

DATABASE_URL=postgresql://signia:una_contraseña_que_tú_elijas@postgres:5432/signia

JWT_SECRET=una_clave_larga_y_privada

POSTGRES_USER=signia

POSTGRES_DB=signia

```

La contraseña de `POSTGRES_PASSWORD` y la que aparece dentro de `DATABASE_URL` deben ser **la misma**. Luego:

```bash

docker compose up -d --build --wait

```

La primera vez puede tardar varios minutos porque descarga e instala las dependencias de visión por computador. Cuando termine, abre **http://localhost:5173** en el navegador y crea tu cuenta. Los pasos detallados, otras formas de ejecutarlo y las soluciones a los problemas más comunes están en las secciones siguientes.

## Funcionalidades del proyecto

Las siguientes funcionalidades cuentan con componentes y rutas en el código de la rama `develop` revisada. Algunas requieren permisos de administrador, una cámara o servicios externos configurados para utilizarse por completo.

### Usuarios y autenticación

- **Registro de cuentas:** permite crear un usuario desde la plataforma, con validación de los datos ingresados.
- **Inicio y cierre de sesión:** se utiliza correo y contraseña; el backend genera tokens JWT y permite revocarlos al cerrar sesión.
- **Control de acceso:** se diferencian los roles `usuario` y `administrador`. También hay controles para intentos fallidos, bloqueo temporal de cuentas y límite de solicitudes al iniciar sesión.
- **Recuperación de contraseña:** existen pantallas y endpoints para solicitar un enlace de recuperación y establecer una nueva contraseña. El envío de correos requiere configurar el servicio correspondiente.
- **Administración de usuarios:** los administradores pueden consultar usuarios, buscar registros, cambiar roles, desactivar o reactivar cuentas y consultar su progreso.

### Aprendizaje y práctica del alfabeto LSC

- **Consulta del alfabeto:** muestra las letras disponibles, sus imágenes y descripciones. Se pueden buscar letras y consultar su información.
- **Edición de letras:** los administradores pueden actualizar información de las letras desde el módulo de aprendizaje.
- **Práctica libre:** permite utilizar la cámara para practicar distintas letras sin seleccionar una letra objetivo.
- **Práctica específica:** permite elegir una letra desde el módulo Aprender y practicarla con la cámara.
- **Reconocimiento de señas:** utiliza OpenCV y MediaPipe para procesar imágenes de la mano, con lógica separada para reconocimiento estático y con movimiento.
- **Registro de sesiones y resultados:** el backend permite iniciar y finalizar sesiones, registrar resultados y consultar los intentos asociados a un usuario.
- **Seguimiento del aprendizaje:** consulta qué letras están pendientes o aprendidas, y calcula el porcentaje de avance en el perfil. La pantalla también muestra intentos, aciertos y precisión, junto con controles visuales de preferencias y una meta diaria seleccionable; esos controles de preferencias se manejan actualmente dentro del componente de la página.
- **Aprendizaje por aciertos:** después de registrar un resultado correcto, el servicio evalúa los intentos exitosos acumulados de esa letra. El mínimo predeterminado es **tres aciertos**, configurable mediante `APRENDIZAJE_MIN_ACIERTOS`.
- **Historial de práctica:** permite consultar registros de reconocimiento del usuario y mostrar información de su actividad durante la práctica.

El reconocimiento depende de la cámara y de las condiciones de captura; los resultados pueden variar según la posición de la mano, el movimiento y la calidad de la imagen.

## Tecnologías utilizadas

| Área | Tecnologías |
| --- | --- |
| Frontend | React, TypeScript, Vite, React Icons |
| Backend | Python 3.12, FastAPI, Uvicorn, Pydantic |
| Visión por computador | OpenCV, MediaPipe |
| Base de datos | PostgreSQL 16, Psycopg |
| Autenticación | JWT, hash de contraseñas con Argon2 |
| Contenedores | Docker, Docker Compose, Nginx |
| Pruebas y calidad | pytest, pytest-cov, Ruff, Vitest, React Testing Library, ESLint, SonarQube, Radon |
| Automatización | GitHub Actions, Docker Hub |

## Organización del proyecto

La aplicación se divide en frontend, backend y base de datos. El frontend presenta las pantallas y envía solicitudes HTTP; el backend valida las solicitudes, administra los datos y realiza el procesamiento de visión. PostgreSQL almacena la información de los usuarios, letras, sesiones y avances.

```text

FIS_2630_1204_G4/

├── .github/workflows/           # Pruebas, métricas, Docker, publicación y automatizaciones

├── app/

│   ├── main.py                  # Inicio y configuración de FastAPI

│   ├── routes/                  # Endpoints de la API

│   ├── services/                # Funciones del sistema y reglas de negocio

│   ├── repositories/            # Consultas de datos para aprendizaje

│   ├── vision/                  # Detección de manos y reconocimiento

│   └── assets/alfabeto/         # Imágenes del alfabeto

├── conf/                        # Base de datos, configuración y registros

├── database/

│   ├── schema.sql               # Esquema de PostgreSQL

│   ├── seed.sql                 # Datos iniciales para pruebas

│   └── migrations/              # Cambios adicionales de la base de datos

├── src/

│   ├── front/

│   │   ├── srcFront/            # Pantallas, componentes, hooks y servicios de React

│   │   ├── tests/               # Pruebas del frontend

│   │   ├── package.json

│   │   └── Dockerfile

│   ├── schemas/                  # Validación de entrada y salida del backend

│   └── tests/                   # Pruebas del backend

├── docs/                        # Diagramas, arquitectura, pruebas y despliegue

├── scripts/                     # Utilidades y pruebas manuales

├── Dockerfile                   # Imagen del backend

├── docker-compose.yml           # Ejecución del sistema completo

├── docker-compose.validacion.yml # Ejecución desde imágenes publicadas

├── .env.example                 # Plantilla de configuración

├── .env.validacion.example      # Plantilla para validación externa

├── requirements.txt             # Dependencias de Python

├── requirements.lock.txt        # Dependencias fijadas

├── sonar-project.properties     # Configuración de análisis de calidad

└── README.md

```

## Ejecución con Docker Compose

Esta es la opción más sencilla para ejecutar el frontend, el backend y PostgreSQL en un solo computador.

### Requisitos

- Git.
- Docker Engine o Docker Desktop, con Docker Compose disponible mediante `docker compose`.
- Conexión a Internet para descargar las imágenes y dependencias cuando sea necesario.

### 1. Obtener el repositorio

```bash

git clone https://github.com/puj-course/FIS_2630_1204_G4.git

cd FIS_2630_1204_G4

```

### 2. Configurar las variables de entorno

En Linux o WSL:

```bash

cp .env.example .env

```

En PowerShell:

```powershell

Copy-Item .env.example .env

```

Abre `.env` y configura, como mínimo, los datos de PostgreSQL y la clave JWT. Para usar **PostgreSQL del mismo Docker Compose**, la conexión debe apuntar al servicio `postgres`, no a `localhost` ni a una instancia de Neon:

```dotenv

POSTGRES_USER=signia

POSTGRES_PASSWORD=CAMBIAR_POR_CONTRASENA_PROPIA

POSTGRES_DB=signia

DATABASE_URL=postgresql://signia:CAMBIAR_POR_CONTRASENA_PROPIA@postgres:5432/signia

JWT_SECRET=GENERAR_UNA_CLAVE_LARGA_Y_PRIVADA

JWT_EXPIRE_MINUTES=60

APRENDIZAJE_MIN_ACIERTOS=3

```

La contraseña de `POSTGRES_PASSWORD` debe coincidir con la incluida en `DATABASE_URL`. Los valores anteriores son ejemplos; no deben utilizarse como contraseñas definitivas. El `.env` es privado y no debe subirse a GitHub.

La recuperación de contraseña necesita variables adicionales para el correo. Todas las variables, con su explicación, están en [Variables de configuración](#variables-de-configuración).

Si se utiliza una base de datos alojada externamente, `DATABASE_URL` debe apuntar a esa base, pero el servicio `postgres` de Compose seguirá iniciándose por la configuración actual.

### 3. Construir y levantar los servicios

```bash

docker compose up -d --build --wait

```

Para comprobar su estado:

```bash

docker compose ps

```

Cuando terminen de iniciar, estarán disponibles estas direcciones:

| Servicio | Dirección |
| --- | --- |
| Aplicación web | http://localhost:5173 |
| Backend | http://localhost:8000 |
| Documentación interactiva de la API | http://localhost:8000/docs |
| Estado del backend | http://localhost:8000/health |
| PostgreSQL, desde el computador | `localhost:5432` |

El archivo `docker-compose.yml` define tres servicios: `frontend`, `backend` y `postgres`. PostgreSQL conserva los datos en un volumen de Docker y ejecuta el esquema, las migraciones y las inserciones de prueba durante la primera inicialización de un volumen nuevo.

Para consultar registros de los servicios:

```bash

docker compose logs --tail=100 backend

```

Para detenerlos sin borrar los datos:

```bash

docker compose down

```

**Precaución:** `docker compose down -v` también elimina los volúmenes del proyecto, incluida la información de PostgreSQL almacenada allí.

### 4. Abrir SignIA y comprobar que funciona

1. Abre http://localhost:8000/health. Debe responder que el backend está en funcionamiento.
2. Abre http://localhost:5173. Debe aparecer la pantalla **Iniciar sesión**.
3. Crea una cuenta nueva y entra (ver [Cómo usar SignIA](#cómo-usar-signia)).

La cámara solo funciona si abres la aplicación desde `localhost` o desde una dirección `https`. Si la abres usando la IP de tu computador, el navegador no dejará usar la cámara.

**Cómo obtener una cuenta de administrador:** al registrarse, todas las cuentas nuevas tienen el rol `usuario`. Para convertir una cuenta en administrador, cámbiale el rol en la base de datos (cambia el correo por el tuyo):

```bash

docker compose exec postgres psql -U signia -d signia -c "UPDATE usuarios SET rol = 'administrador' WHERE correo = 'tu_correo@ejemplo.com';"

```

Si cambiaste `POSTGRES_USER` o `POSTGRES_DB` en `.env`, usa esos mismos valores en lugar de `signia`. Después de que exista un administrador, ese usuario puede cambiar los roles de otras cuentas desde **Administrar usuarios**.

## Ejecución desde imágenes de Docker Hub

El proyecto publica imágenes separadas para el backend y el frontend:

- [Backend en Docker Hub](https://hub.docker.com/r/thejuan127/signia-backend)
- [Frontend en Docker Hub](https://hub.docker.com/r/thejuan127/signia-frontend)

El workflow de publicación genera una etiqueta de versión a partir del tag de Git, por ejemplo `v1.0.0`, y otra etiqueta `latest`. Para ejecutar una versión publicada usando el **Compose principal**, conserva el `.env` configurado y define estas variables antes de descargar las imágenes:

```bash

export SIGNIA_IMAGEN_BACKEND=thejuan127/signia-backend

export SIGNIA_IMAGEN_FRONTEND=thejuan127/signia-frontend

export SIGNIA_TAG=v1.0.0

docker compose pull backend frontend

docker compose up -d --no-build --wait

```

En PowerShell, las variables se establecen con `$env:SIGNIA_IMAGEN_BACKEND`, `$env:SIGNIA_IMAGEN_FRONTEND` y `$env:SIGNIA_TAG`. La etiqueta debe existir realmente en Docker Hub; puede usarse `latest` si se quiere descargar la imagen que tenga esa etiqueta. La opción `--no-build` evita reconstruir las imágenes desde el código.

### Validación externa en otro computador

El repositorio también incluye `docker-compose.validacion.yml` y `.env.validacion.example` para ejecutar SignIA con una base de datos de prueba independiente. Para utilizar esa configuración se necesitan el archivo Compose, la plantilla de entorno y los archivos SQL de `database/`.

En Linux, desde la raíz del proyecto:

```bash

cp .env.validacion.example .env.validacion

```

Se deben completar las contraseñas de prueba en `.env.validacion`, haciendo coincidir `POSTGRES_PASSWORD` con la contraseña incluida en `DATABASE_URL`. Después:

```bash

docker compose --env-file .env.validacion -f docker-compose.validacion.yml pull

docker compose --env-file .env.validacion -f docker-compose.validacion.yml up -d --no-build

docker compose --env-file .env.validacion -f docker-compose.validacion.yml ps

```

Esta configuración descarga las imágenes de Docker Hub y mantiene los datos de PostgreSQL en un volumen independiente. Para validar el despliegue se comprueba la respuesta de `/health`, se abre la interfaz y se realiza una consulta del alfabeto. El equipo realizó una validación de este tipo en un segundo computador Linux.

## Ejecución para desarrollo sin contenedores

Esta alternativa permite modificar el frontend o el backend y comprobar los cambios directamente. Requiere **Python 3.12**, **Node.js 24** (recomendado para ejecutar también las pruebas con la versión de Vitest instalada), npm y una base de datos PostgreSQL disponible. Para la compilación con Docker, el Dockerfile del frontend utiliza Node 20.

### Backend

Desde la raíz del repositorio:

```bash

python3.12 -m venv .venv

source .venv/bin/activate

python -m pip install -r requirements.txt

```

En Windows se puede crear el entorno con `py -3.12 -m venv .venv` y activarlo con `.venv\Scripts\Activate.ps1` en PowerShell.

Si no tienes PostgreSQL instalado, puedes levantar solo la base de datos con Docker (`docker compose up -d postgres`). Después configura `.env` con la conexión PostgreSQL accesible desde el sistema donde ejecutes Python. Si PostgreSQL está en un contenedor publicado en el puerto 5432, normalmente la dirección será `localhost:5432`, en lugar de `postgres:5432` (que corresponde a la red interna de Docker Compose).

```bash

uvicorn app.main:app --reload

```

Para comprobar la API: http://127.0.0.1:8000/docs.

### Frontend

En otra terminal:

```bash

cd src/front

npm ci

npm run dev

```

Vite muestra en la terminal la dirección del servidor de desarrollo. El frontend utiliza `VITE_API_URL` para determinar la dirección del backend; la plantilla está en `src/front/.env.example` (cópiala a `src/front/.env`) y su valor local habitual es `http://127.0.0.1:8000`. Si no la defines, usa ese mismo valor. Con el backend y el frontend en marcha, abre la dirección que muestre Vite (normalmente http://localhost:5173).

## Variables de configuración

SignIA se configura con variables de entorno. Se guardan en un archivo `.env` en la raíz del proyecto, que se crea copiando `.env.example`. Ese archivo **es privado y no se sube a GitHub**.

Esta tabla muestra el nombre de cada variable y para qué sirve. **Los valores reales nunca se escriben en este README.**

### Base de datos

| Variable | ¿Obligatoria? | Para qué sirve |
| --- | --- | --- |
| `POSTGRES_USER` | Con Docker Compose (por defecto `signia`) | Usuario con el que se crea la base de datos de PostgreSQL |
| `POSTGRES_PASSWORD` | Sí, con Docker Compose | Contraseña de ese usuario. Docker Compose no inicia si falta |
| `POSTGRES_DB` | Con Docker Compose (por defecto `signia`) | Nombre de la base de datos |
| `DATABASE_URL` | Sí | Dirección de conexión que usa el backend para llegar a PostgreSQL. Con Docker Compose apunta al servicio `postgres`; sin Docker, a `localhost` o al servidor que uses |

### Seguridad y sesiones

| Variable | ¿Obligatoria? | Para qué sirve |
| --- | --- | --- |
| `JWT_SECRET` | Sí | Clave con la que el backend firma los tokens de inicio de sesión. Debe ser larga y privada |
| `JWT_EXPIRE_MINUTES` | No (por defecto `60`) | Minutos que dura una sesión antes de que el usuario deba entrar de nuevo |

### Aprendizaje

| Variable | ¿Obligatoria? | Para qué sirve |
| --- | --- | --- |
| `APRENDIZAJE_MIN_ACIERTOS` | No (por defecto `3`) | Cantidad de aciertos que necesita un usuario para considerar aprendida una letra. Debe ser un número entero mayor que cero. No aparece en `.env.example`, pero puedes agregarla al `.env` |

### Recuperación de contraseña (correo)

Solo se necesitan si quieres que funcione el envío de correos para recuperar la contraseña. Sin ellas, el resto de la plataforma funciona.

| Variable | Para qué sirve |
| --- | --- |
| `CORREO_TRANSPORTE` | Forma de enviar el correo: `smtp` o `graph` (Microsoft Graph) |
| `SMTP_HOST` | Servidor de correo (SMTP) |
| `SMTP_PORT` | Puerto del servidor de correo (por ejemplo `587`) |
| `SMTP_SECURITY` | Tipo de seguridad de la conexión, por ejemplo `starttls` |
| `SMTP_USER` | Usuario de la cuenta de correo que envía los mensajes |
| `SMTP_PASSWORD` | Contraseña o clave de aplicación de esa cuenta |
| `SMTP_FROM` | Dirección que aparece como remitente |
| `RECUPERACION_URL` | Dirección de la página de la plataforma a la que lleva el enlace del correo |
| `MICROSOFT_CLIENT_ID` | Identificador de la aplicación en Microsoft, solo si se usa `graph` |

### Registros del sistema

| Variable | ¿Obligatoria? | Para qué sirve |
| --- | --- | --- |
| `LOG_LEVEL` | No (por defecto `INFO`) | Nivel de detalle de los mensajes del backend (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

### Frontend

| Variable | ¿Obligatoria? | Para qué sirve |
| --- | --- | --- |
| `VITE_API_URL` | No (por defecto `http://127.0.0.1:8000`) | Dirección del backend a la que se conecta la página. Se define en `src/front/.env` (plantilla en `src/front/.env.example`) y se incorpora **al construir** el frontend, no mientras se ejecuta |

### Otros archivos de configuración

- `.env.validacion.example`: plantilla para probar SignIA con las imágenes de Docker Hub en otro computador (ver [Validación externa en otro computador](#validación-externa-en-otro-computador)).
- `conf/environment.example`: ejemplo de la variable `APRENDIZAJE_MIN_ACIERTOS`.

## Cómo usar SignIA

Estos son los pasos básicos para una persona que usa la plataforma por primera vez. Antes, SignIA debe estar funcionando (ver [Inicio rápido](#inicio-rápido)) y debes abrir **http://localhost:5173** en un navegador con cámara.

### 1. Registrarse

1. En la pantalla **Iniciar sesión**, elige la opción para crear una cuenta (registro).
2. Escribe tu nombre completo, tu correo electrónico y una contraseña, y confirma la contraseña.
   - El nombre debe tener entre 2 y 100 caracteres.
   - La contraseña debe tener **mínimo 12 caracteres**.
   - Las dos contraseñas deben ser iguales.
3. Envía el formulario. Verás el mensaje **Cuenta creada**.

### 2. Iniciar sesión

1. Escribe tu correo y tu contraseña en **Iniciar sesión**.
2. Si olvidaste la contraseña, usa la opción de recuperación. Esta opción necesita que el correo esté configurado (ver [Variables de configuración](#variables-de-configuración)).
3. Al entrar verás **Bienvenido a SignIA**. El botón **¿Cómo funciona?** muestra una explicación corta de la plataforma.

El menú de la izquierda tiene las secciones **Aprender**, **Practicar** y **Perfil**, además de **Ayuda** y **Cerrar sesión**.

### 3. Aprender el alfabeto

1. Entra a **Aprender**.
2. Verás las letras del alfabeto con su imagen y su descripción. Puedes escribir en **Buscar letra...** para encontrar una.
3. Elige una letra para ver cómo se hace la seña y sus instrucciones.

### 4. Practicar con la cámara

1. Entra a **Practicar**. Aparece la pregunta **¿Cómo quieres practicar?** con dos opciones:
   - **Práctica libre:** practicas cualquier letra sin elegir una antes.
   - **Práctica específica:** vas a **Aprender**, eliges una letra y pulsas **Practicar** (o **Practicar esta letra**).
2. Pulsa **Activar cámara** y permite el uso de la cámara cuando el navegador te lo pida.
3. Elige el tipo de reconocimiento: **Letra estática** (la seña no se mueve) o **Letra con movimiento**.
4. Haz la seña frente a la cámara, con la mano bien iluminada y dentro del cuadro. SignIA mostrará la letra que reconoce.
5. Cuando termines, pulsa **Apagar cámara**.

Cada letra que aciertas la cantidad de veces configurada (por defecto, tres) se marca como aprendida.

### 5. Revisar tu avance

En **Perfil** puedes ver tu porcentaje de avance, las letras aprendidas y pendientes, tus intentos, aciertos y precisión, y elegir una meta diaria de práctica.

### 6. Funciones para administradores

Si tu cuenta tiene el rol `administrador`:

- En **Aprender** puedes usar **Editar instrucciones** para cambiar la descripción de una letra y **Guardar cambios**.
- En **Administrar usuarios** puedes buscar usuarios, cambiar su rol, desactivar o reactivar cuentas y consultar su progreso.

## Pruebas y calidad

### Backend

Las pruebas se encuentran en `src/tests/`. Para ejecutarlas desde la raíz del proyecto, con Python y las dependencias instaladas:

```bash

python -m pytest src/tests -q

python -m ruff check .

```

Para generar cobertura:

```bash

python -m pytest src/tests --cov=app --cov-report=term-missing

```

Las pruebas que utilizan PostgreSQL necesitan `DATABASE_URL` apuntando a una **base de datos de pruebas**, preparada con el esquema y las migraciones. No se recomienda ejecutar pruebas que escriben datos sobre una base de producción.

Una forma sencilla de tener esa base de pruebas en tu computador es crear una base aparte dentro del PostgreSQL de Docker Compose y cargar el esquema:

```bash

docker compose up -d postgres

docker compose exec postgres createdb -U signia signia_test

docker compose exec -T postgres psql -U signia -d signia_test < database/schema.sql

docker compose exec -T postgres psql -U signia -d signia_test < database/migrations/intentos_reconocimiento.sql

docker compose exec -T postgres psql -U signia -d signia_test < database/migrations/agregar_resultado_a_intentos.sql

export DATABASE_URL=postgresql://signia:TU_CONTRASENA@localhost:5432/signia_test

python -m pytest src/tests -q

```

Cambia `TU_CONTRASENA` por la contraseña de `POSTGRES_PASSWORD`. En PowerShell, la variable se define con `$env:DATABASE_URL = "..."`.

### Frontend

Desde `src/front/`:

```bash

npm ci

npm run lint

npm run build

npm test

npm run test:coverage

```

Las pruebas del frontend utilizan Vitest y React Testing Library. La cobertura se genera en `src/front/coverage/`, una carpeta ignorada por Git.

### GitHub Actions y SonarQube

Los workflows están en `.github/workflows/`:

| Workflow | Función |
| --- | --- |
| `backend-ci.yml` | Ruff, pruebas de Python, cobertura mínima del 80 % y reportes |
| `frontend-ci.yml` | Instalación, ESLint y compilación del frontend |
| `docker-check.yml` | Construcción de las imágenes y verificación de los contenedores |
| `SonarQube.yml` | Pruebas y análisis de calidad del backend y frontend |
| `backend-metrics.yml` | Métricas de complejidad, mantenibilidad, líneas y acoplamiento |
| `cd.yml` | Pruebas, publicación de imágenes en Docker Hub y despliegue en un runner WSL |
| `close-issues-develop.yml` | Cierre de issues referenciadas al integrar cambios |
| `telegram-*.yml` | Avisos del proyecto relacionados con issues, cambios y ejecuciones |

El workflow de CD se activa al publicar un tag con el formato `v*.*.*`. Primero ejecuta las pruebas del backend, luego construye y publica las imágenes del frontend y backend, y finalmente intenta desplegarlas en un **runner propio** etiquetado `signia-wsl`. Esa última etapa requiere que el runner esté disponible y tenga su archivo de entorno preparado; publicar imágenes en Docker Hub no significa que exista una página alojada permanentemente en Internet.

Para conocer el funcionamiento detallado del despliegue, consulta [docs/cd/pipeline_cd.md](docs/cd/pipeline_cd.md).

## Despliegue

SignIA se despliega con contenedores Docker. Hay tres formas de hacerlo, según el caso:

| Caso | Qué hacer | Más información |
| --- | --- | --- |
| Probar o desarrollar en tu computador | `docker compose up -d --build --wait` | [Ejecución con Docker Compose](#ejecución-con-docker-compose) |
| Ejecutar una versión ya publicada, sin compilar | Descargar las imágenes de Docker Hub | [Ejecución desde imágenes de Docker Hub](#ejecución-desde-imágenes-de-docker-hub) |
| Validar en otro computador con una base de datos aparte | Usar `docker-compose.validacion.yml` | [Validación externa en otro computador](#validación-externa-en-otro-computador) |

### Componentes que se despliegan

- **Frontend:** imagen basada en Nginx que sirve la aplicación React ya compilada (puerto `5173`).
- **Backend:** imagen de Python 3.12 con FastAPI, OpenCV y MediaPipe (puerto `8000`).
- **Base de datos:** PostgreSQL 16 con un volumen de Docker para conservar los datos (puerto `5432`).

### Base de datos

La creación inicial de la base de datos (esquema, datos de prueba y migraciones) se documentó en la historia de usuario [Creación inicial de base de datos SignIA (#47)](https://github.com/puj-course/FIS_2630_1204_G4/pull/47). Allí y en [database/README.md](database/README.md) está el paso a paso para preparar PostgreSQL, ya sea el del propio Docker Compose o uno alojado en un servicio externo como Neon. Para ver sus tablas y relaciones, consulta [docs/database.md](docs/database.md) y [database/diagrama-er.md](database/diagrama-er.md).

Con Docker Compose, la base se prepara sola la primera vez que se crea el volumen. Si ya existe un volumen anterior, los scripts de `database/` no se vuelven a ejecutar; en ese caso aplica las migraciones manualmente.

### Despliegue automático

Cuando el equipo publica una etiqueta de versión con el formato `v*.*.*` (por ejemplo `v1.0.0`), GitHub Actions ejecuta las pruebas del backend, publica las imágenes en Docker Hub y las despliega en un computador del equipo con un runner propio. Publicar las imágenes no significa que exista una página abierta permanentemente en Internet. El funcionamiento completo está en [docs/cd/pipeline_cd.md](docs/cd/pipeline_cd.md).

### Consideraciones antes de desplegar en otro lugar

- Usa contraseñas y un `JWT_SECRET` propios y distintos a los de desarrollo.
- La dirección del backend (`VITE_API_URL`) se fija al construir el frontend. Si el backend no estará en `http://127.0.0.1:8000`, reconstruye el frontend con la dirección correcta.
- El backend solo acepta peticiones desde `localhost` y `127.0.0.1` en los puertos `3000` y `5173` (lista `origenes_permitidos` en `app/main.py`). Si publicas la página en otra dirección, agrégala a esa lista.
- La cámara necesita `localhost` o una dirección `https`.
- Para ver el esquema general, consulta el [diagrama de despliegue](docs/diagramas/diagrama-despliegue.md).

## Base de datos

El almacenamiento principal se realiza en PostgreSQL. El esquema define las tablas `usuarios`, `letras`, `sesiones_reconocimiento`, `resultados_reconocimiento`, `progreso_usuario`, `recuperaciones_contrasena` y `tokens_revocados`. La migración `database/migrations/intentos_reconocimiento.sql` incorpora la tabla `intentos_reconocimiento`, utilizada para registrar y consultar intentos individuales.

Las relaciones permiten asociar cada sesión con un usuario, los resultados con sus sesiones y letras, y el progreso con cada usuario y letra. Las restricciones evitan, por ejemplo, correos duplicados y cantidades de aciertos superiores a los intentos registrados.

Los archivos principales son:

- `database/schema.sql`: estructura inicial y restricciones.
- `database/seed.sql`: información ficticia para pruebas y letras del alfabeto.
- `database/migrations/`: cambios posteriores del esquema.

La estructura y los datos iniciales se ejecutan automáticamente cuando PostgreSQL inicia con un volumen vacío en Docker Compose. Si la base ya existe, los scripts de inicialización no se vuelven a ejecutar automáticamente; los cambios posteriores requieren aplicar las migraciones correspondientes.

## API del backend

FastAPI organiza sus rutas por módulos. Estos son algunos de los endpoints registrados en `app/main.py`:

| Módulo | Endpoints principales | Uso |
| --- | --- | --- |
| Estado | `GET /health` | Verificar que el backend responde |
| Autenticación | `POST /auth/login`, `POST /auth/registro`, `GET /auth/me`, `POST /auth/logout` | Cuenta y sesión del usuario |
| Recuperación | `POST /auth/recuperar-contrasena`, `POST /auth/restablecer-contrasena` | Recuperación y cambio de contraseña |
| Usuarios | `GET /usuarios`, `POST /usuarios`, `PATCH /usuarios/{id_usuario}/rol` | Administración de usuarios |
| Letras | `GET /letras`, `GET /letras/{id_letra}`, `PATCH /letras/{id_letra}` | Consulta y edición del alfabeto |
| Perfil y progreso | `GET /perfil`, `GET /progreso`, `GET /progreso/letras` | Consulta del avance |
| Visión | `POST /vision/reconocer` | Procesamiento de una imagen para reconocimiento |
| Sesiones y resultados | `/sesiones`, `/resultados`, `/resultados-reconocimiento` | Registro y consulta de prácticas |
| Historial e intentos | `GET /historial`, `GET /intentos` | Consulta de actividad del usuario |

La lista completa, los métodos HTTP, los esquemas de entrada y las respuestas se pueden consultar en **http://localhost:8000/docs** cuando el backend esté ejecutándose. Algunas operaciones requieren un token de usuario y otras permisos de administrador.

## Patrones y organización del código

Durante el desarrollo se aplicaron varios patrones para separar tareas y facilitar el mantenimiento:

- **Strategy:** `app/vision/estrategia_reconocimiento.py` y `app/vision/reconocimiento.py` permiten utilizar reconocimiento estático o con movimiento mediante un contrato común.
- **Singleton:** `app/vision/gestor_detectores.py` administra instancias compartidas de los detectores dentro de un mismo proceso.
- **Decorator:** `app/vision/decoradores_reconocimiento.py` añade la medición del tiempo a las operaciones de reconocimiento.
- **Chain of Responsibility:** `app/services/cadena_autenticacion.py` organiza las comprobaciones relacionadas con el inicio de sesión.
- **Facade:** `app/services/fachada_recuperacion_contrasena.py` reúne las operaciones del flujo de recuperación; en el frontend, `src/front/srcFront/services/FachadaRegistroPractica.ts` coordina el registro de los intentos.
- **Observer:** `src/front/srcFront/events/EventosPractica.ts` permite notificar cambios en la práctica a los componentes que los necesitan.

Además, el frontend mantiene separadas las pantallas, los servicios que consultan la API, los componentes reutilizables y los hooks asociados a la cámara y el reconocimiento.

## Documentación adicional

En `docs/` se conservan los diagramas y documentos del proyecto. Los más útiles para complementar este README son:

- [Arquitectura del backend](docs/architecture.md).
- [Funcionalidades del backend](docs/backend-features.md).
- [Módulos del frontend](docs/frontend.md).
- [Instalación del backend](docs/installation_backend.md).
- [Aprendizaje de letras por intentos](docs/aprendizaje-por-intentos.md).
- [Pipeline de publicación y despliegue](docs/cd/pipeline_cd.md).
- [Documentación de la base de datos](docs/database.md).
- [Diagramas del proyecto](docs/diagramas/).

## Solución de problemas

| Problema | Causa probable | Qué hacer |
| --- | --- | --- |
| Docker dice que falta `POSTGRES_PASSWORD` o `DATABASE_URL` | No existe el archivo `.env` o está incompleto | Copia `.env.example` a `.env` y completa los valores (ver [Inicio rápido](#inicio-rápido)) |
| El backend no se conecta a la base de datos | `DATABASE_URL` mal escrita o con otra contraseña | Con Docker Compose usa `@postgres:5432`, no `localhost`, y la misma contraseña que `POSTGRES_PASSWORD` |
| Cambié la contraseña en `.env` y sigue fallando | PostgreSQL ya guardó la contraseña anterior en su volumen | Si no necesitas los datos, ejecuta `docker compose down -v` y vuelve a levantar. **Esto borra la base de datos** |
| `port is already allocated` o puerto en uso | Otro programa usa el `5173`, `8000` o `5432` | Cierra ese programa (por ejemplo, otra instancia de PostgreSQL en el `5432`) o cambia el puerto en `docker-compose.yml` |
| El primer `docker compose up --build` tarda mucho | Se descargan e instalan OpenCV, MediaPipe y otras dependencias | Es normal la primera vez. Revisa el avance con `docker compose logs -f backend` |
| La página carga, pero no muestra letras ni deja iniciar sesión | El frontend no encuentra el backend | Comprueba http://localhost:8000/health y abre la página desde http://localhost:5173 en el mismo computador |
| Error de CORS en la consola del navegador | Abriste la página desde una dirección no permitida (por ejemplo, la IP del computador) | Usa `localhost:5173` o agrega el origen a `origenes_permitidos` en `app/main.py` |
| El navegador no deja usar la cámara | La página no está en `localhost` ni en `https`, o no diste permiso | Abre `http://localhost:5173` y acepta el permiso de cámara |
| La seña no se reconoce | Poca luz, mano fuera del cuadro o tipo de reconocimiento equivocado | Mejora la iluminación, centra la mano y cambia entre **Letra estática** y **Letra con movimiento** |
| No llega el correo de recuperación | No están configuradas las variables de correo | Completa las variables de [Recuperación de contraseña](#recuperación-de-contraseña-correo) |
| `npm ci` o las pruebas del frontend fallan | Versión de Node distinta | Usa Node.js 24 para desarrollo y pruebas (el Dockerfile usa Node 20 solo para compilar) |
| Las pruebas del backend fallan por la base de datos | `DATABASE_URL` no apunta a una base de pruebas lista | Prepara una base de pruebas con el esquema y las migraciones (ver [Pruebas y calidad](#pruebas-y-calidad)) |

Si ninguna solución funciona, revisa los registros con `docker compose logs --tail=100 backend` y abre un issue en el repositorio con el mensaje de error.

## Trabajo en equipo y contribuciones

| Integrante | Rol |
| --- | --- |
| Isabel Gutiérrez | Scrum Master |
| Juan Diego Arévalo | Product Owner y QA Lead |
| Juan Pablo Vanegas | Sprint Planner |
| David Vallejo | Configuration Manager |
| Óscar Martínez Mantilla | DevOps Engineer |

**Asignatura:** Fundamentos de Ingeniería de Software · **Docente:** Luis Gabriel Moreno Sandoval · **Universidad:** Pontificia Universidad Javeriana.

## Licencia

Proyecto académico. Consulta el archivo [LICENSE](LICENSE) para conocer los términos incluidos en el repositorio.
