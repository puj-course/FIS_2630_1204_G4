# Instalación y ejecución del backend de SignIA

## Descripción general

El backend de SignIA está desarrollado con Python 3.12 y FastAPI. Utiliza PostgreSQL para guardar los datos, y OpenCV y MediaPipe para el reconocimiento de manos. En esta guía se describen dos formas de ponerlo en funcionamiento: ejecutarlo directamente con Python o levantarlo junto con los demás servicios mediante Docker Compose.

## Requisitos previos

Para trabajar con el código se necesita Python 3.12, un gestor de paquetes como `pip` y una instancia de PostgreSQL accesible. Para utilizar la versión en contenedores se necesita Docker con el complemento Docker Compose. Las dependencias Python están declaradas en `requirements.txt`, que incluye `requirements-recuperacion.txt`. `requirements.lock.txt` contiene una lista de versiones fijadas disponible en el proyecto.

## Entorno virtual e instalación

Desde la carpeta raíz del repositorio, en Linux o WSL:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

En Windows PowerShell, con Python 3.12 instalado:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

La instalación de las dependencias de visión puede necesitar bibliotecas del sistema según la distribución de Linux. El Dockerfile contiene las dependencias de sistema utilizadas en la imagen del backend y puede servir como referencia.

## Variables de entorno

En la raíz del repositorio existe `.env.example`, que sirve como punto de partida:

```bash
cp .env.example .env
```

En Windows PowerShell se puede usar `Copy-Item .env.example .env`. Después se deben completar las variables necesarias en el archivo `.env`, que permanece fuera de Git.

| Variable | Uso |
|---|---|
| `DATABASE_URL` | Conexión del backend a PostgreSQL |
| `JWT_SECRET` | Clave de firma de tokens de autenticación |
| `JWT_EXPIRE_MINUTES` | Duración de los tokens, expresada en minutos |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Configuración del servicio PostgreSQL de Docker Compose |
| `APRENDIZAJE_MIN_ACIERTOS` | Mínimo de aciertos para marcar una letra como aprendida; predeterminado `3` |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_SECURITY`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` | Variables del método de envío SMTP, cuando se utiliza |
| `MICROSOFT_CLIENT_ID`, `CORREO_TRANSPORTE`, `RECUPERACION_URL` | Configuración relacionada con el servicio de recuperación y el transporte de correo |

No todas las variables de correo son necesarias para consultar el alfabeto o utilizar el reconocimiento. La recuperación de contraseña sí requiere que el método de envío esté configurado. Para no afectar usuarios reales, es recomendable utilizar credenciales de prueba en un entorno local.

## Base de datos

Antes de trabajar con las rutas que guardan o consultan información, deben existir las tablas y migraciones necesarias. Si se utiliza PostgreSQL directamente, se pueden aplicar los scripts con `psql` en este orden:

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f database/schema.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f database/migrations/intentos_reconocimiento.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f database/migrations/agregar_resultado_a_intentos.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f database/seed.sql
```

Estos comandos corresponden a una base preparada para recibir la estructura desde cero. Para una base que ya existe se debe revisar qué scripts fueron aplicados antes de repetirlos. La explicación de las tablas y su creación está en [database.md](database.md).

## Iniciar el backend con Python

Con el entorno virtual activo y desde la raíz del repositorio:

```bash
python -m uvicorn app.main:app --reload
```

La API responde en `http://localhost:8000` y su documentación interactiva está disponible en `http://localhost:8000/docs`. Para comprobar que el servidor arrancó:

```bash
curl http://localhost:8000/health
```

Este endpoint confirma que el servidor responde, pero no comprueba por sí solo que todas las operaciones de base de datos o correo estén funcionando.

## Ejecutar los servicios con Docker Compose

El proyecto contiene un `Dockerfile` para el backend y `src/front/Dockerfile` para el frontend. El archivo `docker-compose.yml` organiza los tres servicios: PostgreSQL, backend y frontend. Una vez preparado el archivo `.env`, desde la raíz se puede ejecutar:

```bash
docker compose up -d --build
```

Los servicios estarán disponibles normalmente en `http://localhost:8000` para el backend y `http://localhost:5173` para el frontend. Para comprobar sus estados:

```bash
docker compose ps
```

La variable `DATABASE_URL` utilizada dentro del backend debe apuntar a una base accesible desde su contenedor. Si se quiere utilizar la base PostgreSQL del mismo Compose, el host de la conexión es `postgres`, no `localhost`. Si apunta a Neon, se utiliza la cadena correspondiente a ese servicio externo, cuidando que las credenciales no sean públicas.

La configuración independiente `docker-compose.validacion.yml` se utiliza para ejecutar las imágenes descargadas de Docker Hub durante las pruebas externas. Su archivo `.env.validacion.example` sirve como plantilla y no debe confundirse con el `.env` del entorno principal.

## Pruebas y revisión del código

Las pruebas del backend se encuentran en `src/tests/`. Desde el entorno Python configurado se puede ejecutar:

```bash
python -m ruff check .
python -m pytest src/tests -q
```

Algunas pruebas necesitan una base PostgreSQL de prueba disponible mediante `DATABASE_URL`. El workflow `.github/workflows/backend-ci.yml` prepara PostgreSQL, instala las dependencias, ejecuta Ruff y realiza las pruebas con cobertura.

## Problemas frecuentes

Si aparece `ModuleNotFoundError`, hay que comprobar que el entorno virtual esté activo y que se instalaron las dependencias de `requirements.txt`. Si ocurre un error con `DATABASE_URL`, conviene revisar la dirección, las credenciales y si PostgreSQL está funcionando. Si falla la parte visual, deben revisarse las dependencias de OpenCV y MediaPipe y los requisitos del sistema operativo. Si la recuperación de contraseña devuelve un error de disponibilidad, es necesario revisar la configuración del transporte de correo.

Si Docker muestra que una imagen local no existe y el comando incluye `--no-build`, hay que construirla o utilizar una imagen previamente publicada mediante la configuración adecuada. La opción `--no-build` impide crear las imágenes que faltan.
