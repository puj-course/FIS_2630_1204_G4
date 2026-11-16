# API del backend de SignIA

## Descripción general

El backend de SignIA está desarrollado con FastAPI y recibe las solicitudes que realiza la plataforma para administrar usuarios, consultar las letras del alfabeto LSC, practicar y guardar resultados. Este documento describe las rutas que aparecen en el código de la rama `develop` revisada, principalmente en `app/main.py` y `app/routes/`. La documentación interactiva de cada esquema se puede consultar en `http://localhost:8000/docs` cuando el servicio está en ejecución.

Las rutas protegidas reciben un token en la cabecera `Authorization: Bearer <token>`. Los endpoints administrativos requieren que el usuario tenga el rol `administrador`. Las respuestas pueden incluir errores de validación `422`, además de los errores particulares que se indican en cada ruta.

## Estado y autenticación

| Método | Ruta | Función | Acceso |
|---|---|---|---|
| GET | `/health` | Comprueba que el backend responde | Público |
| POST | `/auth/registro` | Crea una cuenta con rol `usuario` | Público |
| POST | `/auth/login` | Valida las credenciales y devuelve un JWT | Público |
| GET | `/auth/me` | Consulta los datos de la cuenta autenticada | Autenticado |
| POST | `/auth/logout` | Revoca el token utilizado en la sesión | Autenticado |
| POST | `/auth/recuperar-contrasena` | Solicita la recuperación de contraseña por correo | Público |
| POST | `/auth/restablecer-contrasena` | Restablece la contraseña con un token de recuperación | Público |

Las dos rutas de recuperación se incorporan desde `app/routes/autenticacion.py` mediante los routers de recuperación y restablecimiento, de manera que también reciben el prefijo `/auth`.

En el inicio de sesión se envían `correo` y `contrasena`. Cuando las credenciales son correctas, la respuesta contiene `access_token`, `token_type` y los datos básicos del usuario. El login tiene un límite de cinco solicitudes por minuto mediante SlowAPI, además del control de intentos fallidos y bloqueo temporal de cuentas que realiza el servicio de autenticación.

Para registrarse se envían `nombre`, `correo` y `contrasena`, cuya longitud admitida en el esquema es de 12 a 200 caracteres. El correo no puede repetirse. La recuperación de contraseña requiere una configuración válida del servicio de correo para procesar solicitudes.

## Usuarios y administración

| Método | Ruta | Función |
|---|---|---|
| POST | `/usuarios` | Registra usuarios con el rol indicado |
| GET | `/usuarios` | Lista usuarios; admite el parámetro opcional `buscar` |
| PATCH | `/usuarios/{id_usuario}/rol` | Cambia el rol de una cuenta |
| PATCH | `/usuarios/{id_usuario}/desactivar` | Desactiva una cuenta |
| PATCH | `/usuarios/{id_usuario}/reactivar` | Reactiva una cuenta |
| GET | `/usuarios/{id_usuario}/progreso` | Consulta el resumen de progreso de un usuario |

Estas seis rutas requieren permisos de administrador. El backend también impide que el administrador cambie su propio rol o desactive su propia cuenta mediante las rutas correspondientes.

## Alfabeto LSC y perfil

| Método | Ruta | Función | Acceso |
|---|---|---|---|
| GET | `/letras` | Lista letras registradas y activas | Público |
| GET | `/letras/{id_letra}` | Obtiene una letra por identificador | Público |
| PATCH | `/letras/{id_letra}` | Actualiza la descripción o la ruta de imagen | Administrador |
| GET | `/perfil` | Devuelve los datos del usuario y un resumen de su progreso | Autenticado |

`GET /perfil` devuelve los datos de la cuenta y un objeto `progreso`, con totales de letras, intentos, aciertos y el porcentaje de avance. Las imágenes del alfabeto se sirven mediante la ruta estática `/assets` configurada en `app/main.py`.

## Sesiones, resultados e intentos

| Método | Ruta | Función |
|---|---|---|
| GET | `/sesiones` | Consulta las sesiones del usuario |
| POST | `/sesiones` | Inicia una sesión de reconocimiento |
| PATCH | `/sesiones/{id_sesion}/finalizar` | Finaliza una sesión propia |
| POST | `/resultados` | Registra un resultado dentro de una sesión activa |
| GET | `/resultados/sesion/{id_sesion}` | Consulta los resultados de una sesión propia |
| GET | `/intentos` | Consulta los intentos del usuario |
| GET | `/historial` | Consulta las sesiones con sus resultados |

Estas rutas requieren autenticación. La consulta de intentos permite filtrar por `id_letra` y `id_sesion`, ambos opcionales y positivos. El historial devuelve sesiones activas, finalizadas y canceladas, incluso si todavía no tienen resultados.

Para `POST /resultados`, la petición incluye los campos siguientes:

```json
{
  "id_sesion": 1,
  "id_letra_objetivo": 1,
  "id_letra_detectada": 1,
  "confianza": 0.9
}
```

Este ejemplo utiliza identificadores ilustrativos que deben existir en la base de datos. El servicio comprueba que la sesión esté activa, pertenezca al usuario y que ambas letras estén registradas. Calcula si la respuesta fue correcta, guarda resultado e intento en una misma transacción y, cuando corresponde, solicita la evaluación automática del aprendizaje.

## Registro y consulta de reconocimiento

Además del flujo por sesiones, el proyecto conserva estas rutas:

| Método | Ruta | Función |
|---|---|---|
| GET | `/resultados-reconocimiento` | Consulta los resultados de reconocimiento del usuario |
| POST | `/resultados-reconocimiento` | Crea una sesión finalizada y registra un resultado |
| DELETE | `/resultados-reconocimiento` | Elimina los resultados de reconocimiento del usuario |

La petición de `POST /resultados-reconocimiento` contiene `id_letra_objetivo`, `letra_detectada` y `confianza`. **Estos endpoints y los de `/resultados` tienen flujos distintos.** En el código revisado, la integración que guarda el intento y evalúa el aprendizaje se encuentra en `app/services/resultados_service.py`, utilizado por `POST /resultados`. No se debe asumir que las dos rutas registran exactamente la misma información.

## Progreso y aprendizaje

| Método | Ruta | Función |
|---|---|---|
| POST | `/progreso` | Marca una letra como aprendida para el usuario |
| GET | `/progreso` | Consulta el progreso registrado |
| GET | `/progreso/letras` | Consulta el estado de todas las letras activas |
| PATCH | `/progreso/{id_letra}` | Actualiza el estado de aprendizaje de una letra |

Todas requieren autenticación. En `POST /progreso` se envía `{"id_letra": 1}`. En la actualización del estado se envía `{"dominada": true}` o `{"dominada": false}`. El aprendizaje automático por aciertos del flujo de resultados se documenta con mayor detalle en [aprendizaje-por-intentos.md](aprendizaje-por-intentos.md).

## Reconocimiento visual

El endpoint `POST /vision/reconocer` recibe una imagen JPEG o PNG en Base64 y responde con la letra encontrada, o `null` cuando no se identifica ninguna. Permite los modos `estatica` y `movimiento`, y admite un `id_secuencia` opcional para relacionar fotogramas. Su contrato y los límites de entrada se detallan en [endpoint-vision.md](endpoint-vision.md).

## Códigos de respuesta y comprobación

Según la operación, el backend utiliza respuestas como `200` (consulta correcta), `201` (registro creado), `202` (solicitud de recuperación aceptada), `204` (cierre de sesión), `400` (entrada incorrecta), `401` (autenticación inválida), `403` (sin permisos), `404` (recurso inexistente), `409` (conflicto), `422` (validación), `423` (cuenta bloqueada), `429` (límite de solicitudes), `500` (error interno) y `503` (recuperación no disponible).

Se puede comprobar el estado del servicio con:

```bash
curl http://localhost:8000/health
```

Para probar las rutas protegidas y ver los esquemas completos, se recomienda utilizar la documentación de FastAPI en `/docs`, con credenciales de prueba.
