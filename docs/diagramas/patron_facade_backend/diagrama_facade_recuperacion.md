# Diagrama de clases — Patrón Facade en la recuperación de contraseña

<img width="1067" height="815" alt="Diagrama de clases — Patrón Facade en la recuperación de contraseña" src="https://github.com/user-attachments/assets/a37df18a-36ec-45cb-aeae-5675e6ef73cc" />


## Descripción

Este diagrama muestra cómo se aplicó el patrón **Facade** en el backend de SignIA para el flujo de recuperación y restablecimiento de contraseña.

Antes del cambio, las rutas de FastAPI importaban y coordinaban directamente varios servicios: la configuración del correo, la creación de la solicitud, el envío del correo y el restablecimiento. Ahora las rutas dependen de una sola clase, `FachadaRecuperacionContrasena`, que ofrece una interfaz simple y esconde el subsistema.

Archivos de código relacionados:

- `app/services/fachada_recuperacion_contrasena.py`, la fachada.
- `app/routes/recuperacion_contrasena.py` y `app/routes/restablecimiento_contrasena.py`, los clientes.
- `app/services/correo_recuperacion_service.py`, `app/services/recuperacion_service.py` y `app/services/restablecimiento_service.py`, el subsistema.
- `src/tests/test_fachada_recuperacion_contrasena.py`, las pruebas de la fachada.

## Roles del patrón

| Rol (GoF) | Elemento en SignIA | Responsabilidad |
|---|---|---|
| **Client** | `recuperacion_contrasena`, `restablecimiento_contrasena` | Reciben la petición HTTP, validan los datos y traducen el resultado a códigos HTTP. |
| **Facade** | `FachadaRecuperacionContrasena` | Ofrece una interfaz única para el flujo de recuperación y delega en el subsistema. |
| **Subsystem** | `correo_recuperacion_service`, `recuperacion_service`, `restablecimiento_service` | Implementan la configuración y el envío del correo, la creación de la solicitud y el cambio de contraseña. |

## Notación

- **`«utility»`** es el estereotipo estándar de UML para un elemento sin instancias cuyas operaciones son todas estáticas. Se usa para representar **módulos de Python que exponen funciones**: las rutas y los servicios no son clases.
- Las clases reales del diagrama son `FachadaRecuperacionContrasena`, `RecuperacionNoDisponibleError` y `Exception`.

## Elementos

### `FachadaRecuperacionContrasena`

| Operación | Qué hace |
|---|---|
| `verificar_disponibilidad() : ConfiguracionCorreo` | Obtiene la configuración del correo. Si falta, lanza `RecuperacionNoDisponibleError`. |
| `procesar_solicitud(correo, configuracion) : None` | Crea la solicitud de recuperación y, si existe, envía el correo con el enlace. Si ocurre un error, registra solo su tipo, sin exponer el correo ni los tokens. |
| `restablecer_contrasena(token, nueva_contrasena) : None` | Delega en el servicio de restablecimiento. Si el token no es válido, deja pasar `SolicitudRecuperacionInvalidaError`. |

### `RecuperacionNoDisponibleError`

Excepción propia de la fachada. Hereda de `Exception` y envuelve `ConfiguracionCorreoError`, para que la ruta no tenga que conocer el servicio de correo. La ruta la traduce a una respuesta **503**.

### Clientes

- `recuperacion_contrasena.solicitar_recuperacion(...)` llama a `verificar_disponibilidad()` y programa `procesar_solicitud` como tarea en segundo plano. Responde **202** con el mismo mensaje exista o no el correo.
- `restablecimiento_contrasena.confirmar_restablecimiento(...)` llama a `restablecer_contrasena(...)` y responde **200**, **400** (token no válido o vencido) o **500** (error interno).

Cada módulo de ruta tiene una instancia `fachada` de `FachadaRecuperacionContrasena`. La fachada no tiene estado, así que una instancia sirve para todas las peticiones.

## Relaciones

| Relación | Tipo | Significado |
|---|---|---|
| Rutas → `FachadaRecuperacionContrasena` | Asociación dirigida, rol `fachada`, multiplicidad `1` | Cada ruta tiene una referencia a la fachada. |
| `FachadaRecuperacionContrasena` → servicios | Dependencia `«use»` | La fachada llama a las funciones del subsistema. |
| `FachadaRecuperacionContrasena` → `RecuperacionNoDisponibleError` | Dependencia `«create»` | La fachada crea y lanza la excepción. |
| `recuperacion_contrasena` → `RecuperacionNoDisponibleError` | Dependencia `«use»` | La ruta captura la excepción para responder 503. |
| `RecuperacionNoDisponibleError` → `Exception` | Generalización | Es una excepción de Python. |

Ninguna ruta depende directamente de un servicio del subsistema. Eso es lo que muestra el patrón.

## Qué se quedó en las rutas

Las responsabilidades de HTTP no pasaron a la fachada:

- los códigos 202, 400, 422, 500 y 503;
- la cabecera `Cache-Control: no-store`;
- `BackgroundTasks`;
- los mensajes de validación de `RutaRestablecimiento`.

La fachada no sabe nada de HTTP.

## Pruebas

- Las pruebas existentes de las rutas (`test_ruta_recuperacion.py` y `test_restablecimiento.py`) mantienen sus aserciones de comportamiento. Solo cambió el módulo donde se reemplazan las dependencias, que ahora es el de la fachada.
- `test_fachada_recuperacion_contrasena.py` prueba la fachada aislada del subsistema, con 8 pruebas. Comprueba:
  - que se devuelve la configuración y que su error se convierte en `RecuperacionNoDisponibleError`;
  - que se crea la solicitud y se envía el correo;
  - que no se envía el correo si no hay solicitud;
  - que los errores se registran sin exponer el correo ni los tokens;
  - que el restablecimiento se delega y que el token inválido se propaga;
  - que la excepción reexportada es la misma clase del servicio.

## Elementos omitidos

| Omitido | Motivo |
|---|---|
| `RutaRestablecimiento` | Personaliza los errores de validación de FastAPI; no participa en el patrón. |
| Modelos Pydantic (`SolicitudRecuperacion`, `RespuestaRecuperacion`, `SolicitudRestablecimiento`, `RespuestaRestablecimiento`) | Solo aparecen como tipos en las firmas de las rutas. |
| `ConfiguracionCorreo`, `RecuperacionCreada` | Solo aparecen como tipos en las firmas. |
| `ConfiguracionCorreoError`, `SolicitudRecuperacionInvalidaError` | Son excepciones del subsistema. La primera la convierte la fachada; la segunda la reexporta. Se explican en una nota del diagrama. |
| `microsoft_oauth_service` | Lo usa internamente el servicio de correo; la fachada no depende de él. |
| Funciones internas de los servicios | Solo se muestran las que llama la fachada. |
