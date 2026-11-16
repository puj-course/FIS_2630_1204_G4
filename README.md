# SignIA

**Aprender para comunicar, comunicar para incluir.**

[![Backend CI](https://github.com/puj-course/FIS_2630_1204_G4/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/puj-course/FIS_2630_1204_G4/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/puj-course/FIS_2630_1204_G4/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/puj-course/FIS_2630_1204_G4/actions/workflows/frontend-ci.yml)
[![Docker Check](https://github.com/puj-course/FIS_2630_1204_G4/actions/workflows/docker-check.yml/badge.svg)](https://github.com/puj-course/FIS_2630_1204_G4/actions/workflows/docker-check.yml)

## Descripción

SignIA es una plataforma web multiusuario orientada al aprendizaje y reconocimiento del alfabeto de la Lengua de Señas Colombiana (LSC) mediante visión por computador, la plataforma facilita la práctica del alfabeto de la LSC utilizando la cámara del dispositivo, permitiendo identificar las señas realizadas por el usuario y mostrar la letra correspondiente en tiempo real.

SignIA surge como respuesta a las barreras de comunicación existentes entre personas sordas y oyentes y a la necesidad de generar herramientas tecnológicas que permitan ampliar el conocimiento básico de la LSC, la plataforma busca promover el aprendizaje autónomo, la sensibilización frente a la comunidad sorda y el uso de la tecnología como herramienta para contribuir a una comunicación más inclusiva.



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
├── .github/workflows/           # Pruebas, métricas, Docker, publicación y automatizaciones
├── app/
│   ├── main.py                  # Inicio y configuración de FastAPI
│   ├── routes/                  # Endpoints de la API
│   ├── services/                # Funciones del sistema y reglas de negocio
│   ├── repositories/            # Consultas de datos para aprendizaje
│   ├── vision/                  # Detección de manos y reconocimiento
│   └── assets/alfabeto/         # Imágenes del alfabeto
├── conf/                        # Base de datos, configuración y registros
├── database/
│   ├── schema.sql               # Esquema de PostgreSQL
│   ├── seed.sql                 # Datos iniciales para pruebas
│   └── migrations/              # Cambios adicionales de la base de datos
├── src/
│   ├── front/
│   │   ├── srcFront/            # Pantallas, componentes, hooks y servicios de React
│   │   ├── tests/               # Pruebas del frontend
│   │   ├── package.json
│   │   └── Dockerfile
│   ├── schemas/                  # Validación de entrada y salida del backend
│   └── tests/                   # Pruebas del backend
├── docs/                        # Diagramas, arquitectura, pruebas y despliegue
├── scripts/                     # Utilidades y pruebas manuales
├── Dockerfile                   # Imagen del backend
├── docker-compose.yml           # Ejecución del sistema completo
├── docker-compose.validacion.yml # Ejecución desde imágenes publicadas
├── .env.example                 # Plantilla de configuración
├── .env.validacion.example      # Plantilla para validación externa
├── requirements.txt             # Dependencias de Python
├── requirements.lock.txt        # Dependencias fijadas
├── sonar-project.properties     # Configuración de análisis de calidad
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

La recuperación de contraseña necesita variables adicionales para el correo, como `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`, `RECUPERACION_URL` y, según el método de envío, variables de Microsoft Graph. La plantilla `.env.example` contiene sus nombres.

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

Configura `.env` con la conexión PostgreSQL accesible desde el sistema donde ejecutes Python. Si PostgreSQL está en un contenedor publicado en el puerto 5432, normalmente la dirección será `localhost:5432`, en lugar de `postgres:5432` (que corresponde a la red interna de Docker Compose).

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

Vite muestra en la terminal la dirección del servidor de desarrollo. El frontend utiliza `VITE_API_URL` para determinar la dirección del backend; la plantilla está en `src/front/.env.example` y su valor local habitual es `http://127.0.0.1:8000`.

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


## Trabajo en equipo y contribuciones

| Integrante | Rol registrado en el README anterior |
| --- | --- |
| Isabel Gutiérrez | Scrum Master |
| Juan Diego Arévalo | Product Owner y QA Lead |
| Juan Pablo Vanegas | Sprint Planner |
| David Vallejo | Configuration Manager |
| Óscar Martínez Mantilla | DevOps Engineer |

**Asignatura:** Fundamentos de Ingeniería de Software · **Docente:** Luis Gabriel Moreno Sandoval · **Universidad:** Pontificia Universidad Javeriana.

## Licencia

Proyecto académico. Consulta el archivo [LICENSE](LICENSE) para conocer los términos incluidos en el repositorio.
