# Arquitectura del Backend

## Descripción general

El backend de SignIA está desarrollado utilizando una arquitectura basada en capas, donde se separan las responsabilidades de rutas, lógica de negocio, validación de datos, seguridad, persistencia y procesamiento visual.

La comunicación general del sistema sigue el flujo:
Cliente -> Routes -> Services -> Base de datos / Módulo de visión -> Respuesta HTTP

Esta separación permite mantener el código organizado y facilitar la incorporación de nuevas funcionalidades.

------------------------------------------------------------------------

## Estructura principal

```text
app/
├── main.py
├── security.py
├── limiter.py
├── routes/
├── services/
├── repositories/
└── vision/
conf/
├── config.py
├── database.py
└── logging_config.py
src/
├── schemas/
└── tests/
database/
├── schema.sql
├── seed.sql
└── migrations/
```

`app/main.py` crea la aplicación FastAPI, registra los routers, configura CORS y el control de solicitudes, publica los recursos de `/assets` y libera los detectores al cerrar el servidor. También expone `GET /health` para comprobar que el backend responde.

## Rutas y servicios

Los archivos de `app/routes/` definen las entradas de la API. En la versión revisada están presentes las rutas de autenticación, usuarios, letras, perfil, visión, sesiones, resultados, resultados de reconocimiento, intentos, progreso e historial. Los routers de recuperación y restablecimiento de contraseña se incluyen desde el router de autenticación.

La lógica principal se ubica en `app/services/`. Allí se encuentran los servicios de usuarios, autenticación, recuperación de contraseña, letras, perfil, visión, sesiones, resultados, intentos, historial, progreso y aprendizaje. Por ejemplo, `resultados_service.py` comprueba la sesión y registra el resultado y el intento, mientras que `aprendizaje_service.py` evalúa si el usuario alcanzó el mínimo de aciertos.

La carpeta `app/repositories/` contiene el repositorio utilizado para contar aciertos y registrar aprendizajes. Otras consultas SQL se realizan actualmente desde servicios del backend con ayuda de `conf/database.py`, por lo que no debe describirse toda la persistencia como si estuviera implementada en repositorios independientes.

## Esquemas, configuración y base de datos

Los esquemas de `src/schemas/` validan los datos recibidos y las respuestas de los endpoints. Incluyen modelos de autenticación, usuarios, letras, visión, sesiones, resultados, progreso, intentos e historial.

La conexión con PostgreSQL se realiza mediante Psycopg en `conf/database.py` y utiliza `DATABASE_URL`. `conf/config.py` consulta la configuración del mínimo de aciertos, mientras que `conf/logging_config.py` organiza los registros de la aplicación. Las tablas, sus restricciones y las migraciones se encuentran en `database/`. Para ver el detalle puede consultarse [database.md](database.md).

## Reconocimiento visual

El flujo comienza en `app/routes/vision.py`, continúa en `app/services/vision_service.py` y llega a `app/vision/`. Primero se valida y decodifica la imagen con OpenCV, después se utiliza el detector de mano y finalmente se selecciona el reconocimiento estático o el reconocimiento con movimiento. El modo estático revisa las consonantes y, cuando no encuentra una coincidencia, las vocales. El modo con movimiento utiliza el historial de fotogramas de la secuencia enviada.

Dentro del módulo se encuentran `detector.py`, `gestor_detectores.py`, `reconocimiento.py`, `estrategia_reconocimiento.py`, `letras_estaticas.py`, `letras_movimiento.py`, `vocales.py` y `decoradores_reconocimiento.py`. El directorio `models/` contiene el modelo utilizado por el detector.

## Organización mediante patrones

En el backend pueden identificarse las siguientes decisiones de diseño:

- **Strategy:** `ReconocimientoEstatico` y `ReconocimientoMovimiento` comparten el contrato de `EstrategiaReconocimiento`.
- **Singleton:** `GestorDetectoresCompartido` administra y reutiliza los detectores dentro de un proceso de la aplicación.
- **Decorator:** `DecoradorMedicionTiempo` envuelve el reconocimiento para registrar su duración.
- **Chain of Responsibility:** `cadena_autenticacion.py` divide la comprobación del usuario, el bloqueo y la contraseña en varios manejadores.
- **Facade:** `FachadaRecuperacionContrasena` reúne operaciones relacionadas con el flujo de recuperación de contraseña.

Los patrones Facade y Observer utilizados en algunos componentes React pertenecen al frontend y no se incluyen aquí como implementación del backend.

## Seguridad y ejecución

`app/security.py` se encarga de crear y verificar tokens JWT, consultar el usuario autenticado, exigir permisos administrativos y gestionar tokens revocados. La ruta de login utiliza un límite de solicitudes definido con SlowAPI. El servidor se inicia con `uvicorn app.main:app`, y cuando se ejecuta mediante Docker Compose trabaja junto al frontend y PostgreSQL.

La estructura completa de endpoints se encuentra en [api.md](api.md) y los pasos para ejecutar el backend en [installation_backend.md](installation_backend.md).
