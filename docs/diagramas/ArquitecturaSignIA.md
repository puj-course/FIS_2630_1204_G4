# Arquitectura de SignIA — Modelo C4

Estos diagramas describen la arquitectura general de SignIA con el modelo C4. El nivel 1 presenta el sistema y su entorno, el nivel 2 los contenedores que se ejecutan por separado y el nivel 3 los componentes internos del backend y del frontend. El nivel 4 (código) de cada módulo se documenta en los diagramas de patrones de cada integrante.

## Nivel 1: contexto

```mermaid
%%{init: {'theme': 'neutral'}}%%
flowchart LR
    Visitante["Visitante sin cuenta"]
    Usuario["Usuario aprendiz"]
    Admin["Administrador"]
    Camara["Cámara web"]

    SignIA["SignIA<br/>Aprendizaje y reconocimiento<br/>del alfabeto LSC"]

    Entra["Microsoft Entra ID<br/>identidad OAuth2"]
    Correo["Microsoft Graph o SMTP<br/>envío de correo"]
    Buzon["Buzón del usuario"]

    Visitante -->|"Se registra, inicia sesión<br/>y recupera su contraseña"| SignIA
    Usuario -->|"Practica señas y<br/>consulta su progreso"| SignIA
    Admin -->|"Gestiona usuarios y letras"| SignIA
    Camara -->|"Captura de video local"| SignIA
    SignIA -->|"Obtiene token OAuth2<br/>MSAL por HTTPS"| Entra
    SignIA -->|"Envía correo de recuperación<br/>HTTPS o SMTP 587"| Correo
    Correo -->|"Entrega el enlace<br/>de restablecimiento"| Buzon
```

SignIA se representa como una sola caja. Las tres personas acceden desde el navegador; los servicios de Microsoft solo intervienen en la recuperación de contraseña.

- **Visitante sin cuenta:** puede registrarse, iniciar sesión y solicitar la recuperación de su contraseña.
- **Usuario aprendiz:** rol `usuario`. Practica el alfabeto con la cámara y consulta su progreso.
- **Administrador:** rol `administrador`. Gestiona usuarios (rol, desactivación, progreso) y edita la información de las letras.
- **Correo:** el transporte por defecto es Microsoft Graph (`CORREO_TRANSPORTE=graph`); SMTP es la ruta alternativa.

## Nivel 2: contenedores

```mermaid
%%{init: {'theme': 'neutral'}}%%
flowchart LR
    Persona["Usuario o administrador"] --> Navegador["Navegador"]
    Camara["Cámara web"] -->|"Captura de video local"| SPA

    subgraph SignIA["Sistema SignIA"]
        SPA["Aplicación web<br/>React + TypeScript + Vite<br/>se ejecuta en el navegador"]
        API["API REST<br/>FastAPI + Uvicorn"]
        Vision["Módulo de visión<br/>OpenCV + MediaPipe"]
        PG[("Base de datos<br/>PostgreSQL 16")]
    end

    Correo["Microsoft Graph o SMTP"]

    Navegador -->|"Descarga la SPA<br/>HTTP localhost:5173"| SPA
    SPA -->|"JSON + Bearer JWT<br/>API REST localhost:8000"| API
    SPA -->|"Imágenes de letras<br/>HTTP /assets"| API
    API -->|"Procesa reconocimiento<br/>llamada en proceso"| Vision
    API -->|"SQL · postgres:5432<br/>psycopg 3"| PG
    API -->|"Correo de recuperación<br/>HTTPS o SMTP"| Correo
```

## Contenedores

| Contenedor | Tecnología | Responsabilidad | Comunicación |
|---|---|---|---|
| Aplicación web | React 19, TypeScript, Vite; servida por `nginx:alpine` | Interfaz de aprendizaje, práctica con cámara, perfil y administración | REST hacia la API con JWT en la cabecera `Authorization` |
| API REST | Python 3.12, FastAPI, Uvicorn, PyJWT, slowapi | Autenticación, usuarios, letras, sesiones, resultados, progreso, historial y recuperación | Recibe REST en `8000`; consulta PostgreSQL con SQL |
| Módulo de visión | OpenCV, MediaPipe (`hand_landmarker.task`) | Detecta la mano y reconoce letras estáticas y con movimiento | Llamada en proceso desde `vision_service` |
| Base de datos | PostgreSQL 16, volumen `postgres_data` | Persiste usuarios, letras, sesiones, resultados, intentos, progreso, recuperaciones y tokens revocados | SQL en `postgres:5432`, red interna de Compose |

El módulo de visión se dibuja como contenedor porque tiene una responsabilidad y una tecnología propias, pero **se ejecuta dentro del mismo proceso que la API**. No se despliega por separado ni expone puertos.

## Nivel 3: componentes del backend

```mermaid
%%{init: {'theme': 'neutral'}}%%
flowchart LR
    SPA["Aplicación web"]
    PG[("PostgreSQL")]
    Correo["Microsoft Graph o SMTP"]

    subgraph Backend["API REST de SignIA"]
        Main["Arranque de la aplicación<br/>main.py"]
        Limitador["Límite de solicitudes<br/>limiter.py"]
        Seguridad["Autenticación JWT y roles<br/>security.py"]
        RAcceso["Endpoints de acceso<br/>autenticacion · usuarios · perfil"]
        RAprendizaje["Endpoints de aprendizaje<br/>letras · sesiones · resultados<br/>progreso · historial · intentos"]
        RVision["Endpoint de reconocimiento<br/>vision.py"]
        SAcceso["Lógica de acceso<br/>autenticacion · usuarios · recuperacion<br/>restablecimiento · correo"]
        SAprendizaje["Lógica de aprendizaje<br/>letras · sesiones · resultados<br/>progreso · intentos · historial"]
        Repositorio["Repositorio de aprendizaje<br/>aprendizaje_repository"]
        Vision["Reconocimiento de señas<br/>vision_service + app/vision"]
        Schemas["Contratos de datos<br/>schemas Pydantic"]
        Conf["Configuración y conexión<br/>conf"]
    end

    SPA -->|"Peticiones REST"| Main
    Main -->|"Registra los routers"| RAcceso
    Main -->|"Registra los routers"| RAprendizaje
    Main -->|"Registra el router"| RVision
    RAcceso -->|"Aplica 5 por minuto<br/>en login y registro"| Limitador
    RAcceso -->|"Valida token y rol"| Seguridad
    RAprendizaje -->|"Valida token y rol"| Seguridad
    RAcceso -->|"Delega la lógica"| SAcceso
    RAprendizaje -->|"Delega la lógica"| SAprendizaje
    RVision -->|"procesar_imagen_base64"| Vision
    RAcceso -->|"Valida entrada y salida"| Schemas
    RAprendizaje -->|"Valida entrada y salida"| Schemas
    SAprendizaje -->|"Cuenta aciertos y<br/>registra aprendizaje"| Repositorio
    SAcceso -->|"Obtiene conexión"| Conf
    SAprendizaje -->|"Obtiene conexión"| Conf
    Seguridad -->|"Consulta tokens revocados"| Conf
    Conf -->|"SQL"| PG
    SAcceso -->|"Envía correo de recuperación"| Correo
```

El backend sigue el flujo **router → service → base de datos**. Los routers reciben la petición, delegan la autorización en `security.py` y la lógica en los services. Los services ejecutan SQL directo con psycopg; no hay ORM.

- **Endpoints de acceso:** registro, login, logout, recuperación y restablecimiento de contraseña, gestión de usuarios por el administrador y perfil propio.
- **Endpoints de aprendizaje:** consulta y edición de letras, sesiones de práctica, resultados de reconocimiento, progreso, historial e intentos.
- **Endpoint de reconocimiento:** `POST /vision/reconocer` recibe un fotograma en Base64 y devuelve la letra detectada.
- **Seguridad:** emite y valida JWT HS256 con `jti`, rechaza tokens revocados y expone las dependencias `obtener_usuario_actual` y `requerir_administrador`.
- **Reconocimiento de señas:** contiene los patrones Singleton y Strategy, documentados en `PatronesSingletonStrategy.md`.

## Nivel 3: componentes del frontend

```mermaid
%%{init: {'theme': 'neutral'}}%%
flowchart LR
    subgraph Frontend["Frontend de SignIA"]
        App["Navegación por estado<br/>App"]
        Paginas["Páginas principales<br/>Home · Login · Registro · Aprender<br/>Practica · Perfil · AdminUsuarios"]
        Componentes["Componentes reutilizables<br/>Camara · ResultadoReconocimiento<br/>HistorialReconocimiento · Navbar"]
        Hooks["Cámara y reconocimiento<br/>useCamara · useReconocimiento"]
        Patrones["Lógica de práctica<br/>EventosPractica · FachadaRegistroPractica<br/>ModalidadPractica"]
        Servicios["Servicios por recurso REST<br/>autenticacion · letras · sesiones · resultados<br/>progreso · perfil · usuariosAdmin · vision"]
        Cliente["Cliente HTTP<br/>api.ts"]
    end

    API["API REST"]

    App -->|"Muestra la página activa"| Paginas
    Paginas -->|"Compone la interfaz"| Componentes
    Componentes -->|"Controla cámara y<br/>bucle de reconocimiento"| Hooks
    Componentes -->|"Publica eventos y<br/>registra la práctica"| Patrones
    Paginas -->|"Consulta y envía datos"| Servicios
    Hooks -->|"Envía fotogramas"| Servicios
    Patrones -->|"Coordina servicios"| Servicios
    Servicios -->|"solicitarApi"| Cliente
    Cliente -->|"fetch con JWT"| API
```

El frontend no usa `react-router`: `App` decide qué página mostrar a partir de un estado. Todos los servicios pasan por `api.ts`, que centraliza la URL base (`VITE_API_URL`), la cabecera del token y el manejo de `ErrorApi`.

- **Lógica de práctica:** contiene los patrones Observer y Facade (`PatronesObserverFacade.md`) y Factory Method (`ModalidadPractica`).
- **Estado del cliente:** el JWT y la sesión se guardan en `sessionStorage`; la sesión de reconocimiento, en `localStorage`.

## Decisiones de arquitectura

- **Sin capa de controllers:** los routers de FastAPI llaman directamente a los services. La carpeta `app/controllers/` existe, pero está vacía.
- **SQL directo:** no hay ORM. Los services usan `conf.database.obtener_conexion` y ejecutan las consultas con psycopg 3.
- **Visión en el mismo proceso:** el reconocimiento se ejecuta dentro de la API. Es más simple de desplegar, pero comparte CPU con el resto de endpoints.
- **JWT con revocación:** el token no tiene estado, pero cada uno lleva un `jti` que puede guardarse en `tokens_revocados` para invalidarlo antes de que expire.

## Nota de verificación

Estos diagramas se elaboraron a partir del código de la rama `develop`. El README menciona las carpetas `web/`, `app/controllers/`, `src/models/` y `src/middleware/`, pero el frontend real está en `src/front/srcFront/` y las demás carpetas solo contienen `.gitkeep`. Varios endpoints del backend (`/auth/logout`, `/historial`, `/intentos`, entre otros) están implementados pero el frontend todavía no los consume.
