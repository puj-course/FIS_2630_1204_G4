
# Notificaciones por SMS (Twilio)

Historia de usuario: #615

Además del bot de Telegram ([NotificacionesTelegram.md](NotificacionesTelegram.md)), el equipo recibe mensajes de texto en el celular cuando pasa algo grave o importante en el proyecto. Los envía el workflow `.github/workflows/sms-twilio.yml` a través de la API de Twilio.

Con esto cubrimos el criterio de integración con un servicio SMS: el proveedor es Twilio, cada envío queda registrado en el log de GitHub Actions y en la consola de Twilio, y los mensajes llegan al celular (ver la sección de evidencia).

> Nunca se escribe el SID, el token ni los números de teléfono en el código, en commits o en issues. Solo están en GitHub Secrets.

## Qué se avisa por SMS

| Evento                                              | Mensaje                                                   |
| --------------------------------------------------- | --------------------------------------------------------- |
| Se mergea un pull request en `develop` o `main` | `SignIA: PR #N mergeado en develop por usuario`         |
| Se publica un release                               | `SignIA: release vX.Y.Z publicado`                      |
| Falla Backend CI, SonarQube o el CD                 | `SignIA: FALLO <workflow> en <rama> (failure)`          |
| Termina el CD                                       | `SignIA: CD - Publicar y desplegar SignIA OK en vX.Y.Z` |
| Ejecución manual (`workflow_dispatch`)           | El mensaje de prueba que se escriba                       |

Solo mandamos por SMS estos eventos porque cada mensaje gasta saldo de Twilio. Los pushes, issues y revisiones siguen llegando por Telegram.

Los textos son cortos y sin tildes para que cada uno quepa en un solo SMS de 160 caracteres.

## Cómo funciona

1. Uno de los eventos de la tabla dispara el workflow.
2. El primer paso arma el texto según el tipo de evento.
3. El segundo paso hace un `POST` a `https://api.twilio.com/2010-04-01/Accounts/<SID>/Messages.json` por cada número de `TWILIO_TO`, autenticándose con el SID y el token.
4. Si Twilio responde `201`, el log muestra el `sid` del mensaje y su estado (`queued`). De los números solo se ven los últimos cuatro dígitos (`***1234`).
5. Si algún envío falla, el workflow queda en rojo con el error que devolvió Twilio.

## Configuración

### 1. Cuenta de Twilio

1. Crear la cuenta en https://www.twilio.com/try-twilio.
2. Sacar el número gratuito de prueba en Phone Numbers → Manage → Buy a number. Tiene que poder enviar SMS.
3. Copiar el Account SID y el Auth Token desde la página principal de la consola.
4. Si los mensajes a Colombia fallan, habilitar Colombia en Messaging → Settings → Geo permissions.
5. Verificar el celular de cada persona que va a recibir SMS en Phone Numbers → Manage → Verified Caller IDs, con el formato `+57XXXXXXXXXX`.

> La cuenta de prueba solo envía a números verificados y pone al inicio del mensaje "Sent from your Twilio trial account".

### 2. Secrets del repositorio

Se crean en Settings → Secrets and variables → Actions → New repository secret:

| Secret                 | Valor                                                                    |
| ---------------------- | ------------------------------------------------------------------------ |
| `TWILIO_ACCOUNT_SID` | Account SID (empieza por `AC`)                                         |
| `TWILIO_AUTH_TOKEN`  | Auth Token                                                               |
| `TWILIO_FROM`        | Número de Twilio, ej. `+15551234567`                                  |
| `TWILIO_TO`          | Números destino separados por coma, ej. `+573001112233,+573004445566` |

Los nombres tienen que quedar exactamente así, porque el workflow los lee con esos nombres.

### 3. Probar el envío

1. En Actions → SMS - Avisos con Twilio → Run workflow, lanzar una ejecución manual. Este botón solo aparece cuando el archivo ya está en `main`.
2. Revisar que el workflow termine en verde y que el log tenga una línea como `SMS enviado a ***XXXX | sid=SM... | estado=queued`.
3. Confirmar que el SMS llegó al celular.

## Evidencia

<!-- Agregar capturas -->

- Log de Actions con el `sid` del mensaje.
- Twilio Console → Monitor → Logs → Messaging, con el mensaje en estado `delivered`.
- SMS recibido en el celular.

## Problemas comunes

| Qué pasa                                                         | Por qué                                                | Qué hacer                                           |
| ----------------------------------------------------------------- | ------------------------------------------------------- | ---------------------------------------------------- |
| `HTTP 401 Authenticate`                                         | El SID o el token están mal                            | Crear otra vez los secrets, sin espacios             |
| `The number ... is unverified`                                  | La cuenta es de prueba y el número no está verificado | Verificarlo en Verified Caller IDs                   |
| `Permission to send an SMS has not been enabled for the region` | Colombia no está habilitada                            | Activarla en Geo permissions                         |
| `'From' ... is not a Twilio phone number`                       | `TWILIO_FROM` está mal escrito                       | Copiar el número exacto de la consola, con el `+` |
| No aparece el botón Run workflow                                 | El archivo todavía no está en `main`                | Mergear a `main`                                   |
