# Notificaciones en Telegram

## Objetivo

SignIA avisa automáticamente en el chat de Telegram del equipo cuando pasa algo importante en el repositorio, para que los problemas y los cambios se atiendan más rápido. Los avisos los manda un bot de Telegram desde workflows de GitHub Actions.

Esta guía explica qué avisa cada workflow, qué trae cada mensaje y cómo repetir la configuración desde cero.

> **Importante:** nunca se escribe el token del bot ni el ID del chat en el código, en commits, en issues o en el chat. Solo viven en **GitHub Secrets**, y en este documento aparecen únicamente sus nombres.

---

## Qué se avisa

| Evento en GitHub | Cuándo avisa | Qué trae el mensaje |
|---|---|---|
| Issue | Se crea 🆕, se cierra ✅ o se reabre 🔄 | Título, número, autor y enlace |
| Push | Se hace push a cualquier rama | Rama, autor, commits (los primeros 10, con su autor) y enlace de comparación |
| Pull request | Se abre 🔀, se mergea ✅ o se cierra sin merge ❌ | Título, número, autor, ramas (origen → destino) y enlace. Si se mergeó, también quién lo mergeó |
| Revisión de un pull request | Alguien aprueba 👍, pide cambios 🛠️ o comenta 💬 | Título, número, revisor y enlace |
| Release | Se publica un release 🚀 | Versión, nombre, autor y enlace. Indica si es pre-release |
| CI/CD | Termina Backend CI, Frontend CI o SonarQube | Workflow, resultado (✅ salió bien / ❌ FALLÓ), rama, commit, autor y enlace de la ejecución |

Cosas que **no** avisa:

- Borrado de ramas ni etiquetas (tags).
- Ejecuciones del CI/CD canceladas u omitidas.
- Contenido de los comentarios de las revisiones ni de los releases.

### Ejemplos de mensajes

Issue:

```text
🆕 Issue creada

Título: <título de la issue>
Número: #<número>
Autor: <usuario de GitHub>
Enlace: <enlace a la issue>
```

CI/CD con fallo:

```text
❌ CI/CD: FALLÓ

Workflow: Backend CI
Resultado: FALLO
Rama: <rama>
Commit: <7 primeros caracteres> (<título del commit>)
Autor: <usuario de GitHub>
Enlace: <enlace a la ejecución>
```

---

## Workflows

Los workflows están en `.github/workflows/`:

| Archivo | Eventos que escucha |
|---|---|
| `telegram-issues.yml` | `issues` (`opened`, `closed`, `reopened`) |
| `telegram-push-pr.yml` | `push` (todas las ramas), `pull_request` (`opened`, `closed`) y `pull_request_review` (`submitted`) |
| `telegram-release-ci.yml` | `release` (`published`) y `workflow_run` (`completed`) de **Backend CI**, **Frontend CI** y **SonarQube** |

Cómo funcionan todos:

1. GitHub detecta el evento y arranca el workflow.
2. El workflow arma el mensaje en texto plano con los datos del evento.
3. Envía el mensaje con el método `sendMessage` de la API de Telegram, usando los secrets.

Medidas de seguridad que aplican a los tres:

- Los datos del evento (títulos, nombres de ramas, mensajes de commits) se pasan al script por **variables de entorno**, nunca con `${{ }}` dentro del bloque `run`. Así un título con caracteres raros, como `$(comando)` o comillas, se trata como texto y no se ejecuta.
- Los mensajes son texto plano, para que un título con `<`, `_` o `&` no rompa el envío.
- Los workflows no piden permisos sobre el repositorio (`permissions: {}`).
- Los mensajes se recortan a 4000 caracteres, por debajo del límite de Telegram.
- Si Telegram rechaza el mensaje, el workflow termina en rojo y el error queda visible en la pestaña **Actions**.

### Limitaciones

- Los eventos de `issues` y `workflow_run` solo se ejecutan desde la **rama por defecto del repositorio (`main`)**. Los cambios en esos workflows empiezan a funcionar cuando llegan a `main`.
- Los pull requests que vienen de un fork no tienen acceso a los secrets, así que ese aviso falla. El equipo trabaja con ramas dentro del mismo repositorio.
- Si Backend CI, Frontend CI o SonarQube cambian de nombre, hay que actualizar la lista `workflows:` de `telegram-release-ci.yml`. Los nombres deben ser idénticos.

---

## Configuración paso a paso

Requisitos: una cuenta de Telegram, el chat del equipo y permisos de administrador en el repositorio (para crear secrets).

### 1. Crear el bot

1. En Telegram busca **@BotFather** (el que tiene el check azul de verificado) y toca **Iniciar**.
2. Envía `/newbot`.
3. Escribe el **nombre visible** del bot (puede tener espacios).
4. Escribe el **username**: debe terminar en `bot`, sin espacios ni tildes, y no estar tomado.
5. BotFather responde con el **token**, una línea larga con la forma `números:letras`. Guárdalo solo en un lugar privado.

> Si el token se pega por error en un chat, una issue o un commit, hay que revocarlo: en BotFather envía `/revoke`, elige el bot y actualiza el secret con el token nuevo.

### 2. Agregar el bot al chat del equipo

1. Abre el grupo → nombre del grupo → **Agregar miembros** y busca el username del bot.
2. En el grupo envía un comando o una mención al bot, por ejemplo `/start@<username_del_bot>`. Esto es necesario para poder obtener el ID del chat en el siguiente paso: por defecto un bot en un grupo solo ve comandos y menciones.

### 3. Obtener el ID del chat

El ID se obtiene con el método `getUpdates` de la API de Telegram.

**En PowerShell (Windows)**

```powershell
$TOKEN = Read-Host "Token"
```

Pega el token cuando PowerShell lo pida (lo que va entre comillas es solo el texto de la pregunta, no el valor). Luego:

```powershell
curl.exe -s "https://api.telegram.org/bot$TOKEN/getUpdates"
```

**En Git Bash, Linux o macOS**

```bash
read -s TOKEN
curl -s "https://api.telegram.org/bot$TOKEN/getUpdates"
```

En la respuesta busca el bloque `chat`:

```json
"chat": { "id": <NUMERO_NEGATIVO>, "title": "<nombre del grupo>", "type": "group" }
```

El valor de `id` es el ID del chat. En los grupos es un **número negativo** y hay que copiarlo completo, con el signo menos. Si el grupo se convierte en supergrupo, el ID cambia y hay que actualizar el secret.

Al terminar, borra la variable: `Remove-Variable TOKEN` en PowerShell o `unset TOKEN` en Bash.

**Si `getUpdates` devuelve `"result":[]`**

- Envía de nuevo un mensaje al grupo mencionando al bot (`@<username_del_bot> hola`) y repite la consulta.
- Revisa que no haya un webhook activo: `getWebhookInfo` debe mostrar el campo `url` vacío. Si no lo está, se quita con `deleteWebhook`.
- Las actualizaciones se borran a las 24 horas; manda un mensaje nuevo.
- Si el bot sigue sin ver mensajes, en BotFather usa `/setprivacy`, elige el bot y toca **Disable**; después saca al bot del grupo y vuelve a agregarlo.

### 4. Probar el bot (opcional)

Con el token en `$TOKEN` y el ID del chat a mano, el bot debe poder escribir en el grupo:

```powershell
curl.exe -s -X POST "https://api.telegram.org/bot$TOKEN/sendMessage" -d "chat_id=<ID_DEL_CHAT>" -d "text=Prueba del bot de SignIA"
```

La respuesta debe traer `"ok":true` y el mensaje debe llegar al grupo.

### 5. Crear los GitHub Secrets

En el repositorio: **Settings → Secrets and variables → Actions → New repository secret**. Se crean dos secrets:

| Nombre | Qué contiene |
|---|---|
| `TELEGRAM_TOKEN` | El token que entregó BotFather |
| `TELEGRAM_CHAT_ID` | El ID del chat obtenido con `getUpdates` |

Los nombres deben escribirse exactamente así, porque los workflows los leen con `secrets.TELEGRAM_TOKEN` y `secrets.TELEGRAM_CHAT_ID`. GitHub nunca vuelve a mostrar el valor de un secret; si hay que cambiarlo, se crea de nuevo con el mismo nombre.

### 6. Verificar que funciona

1. Crea una issue de prueba. Debe llegar el aviso 🆕 al grupo.
2. Ciérrala y reábrela. Deben llegar ✅ y 🔄.
3. En la pestaña **Actions** del repositorio, los workflows `Telegram - ...` deben terminar en verde.
4. Cierra o borra la issue de prueba.

---

## Problemas frecuentes

Los errores aparecen en la pestaña **Actions**, dentro de la ejecución del workflow que falló.

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| El workflow termina en rojo con `Unauthorized` | El secret `TELEGRAM_TOKEN` está mal o fue revocado | Crear de nuevo el secret con el token vigente, sin espacios ni saltos de línea |
| El workflow termina en rojo con `chat not found` | El secret `TELEGRAM_CHAT_ID` es incorrecto | Obtener otra vez el ID con `getUpdates` y copiarlo con el signo menos |
| El workflow termina en verde pero no llega el mensaje | El bot salió del grupo, o el grupo cambió de ID | Verificar que el bot siga en el grupo y repetir el paso 3 |
| No aparece ninguna ejecución al crear una issue | El workflow de issues todavía no está en `main`, o Actions está deshabilitado | Verificar el archivo en `main` y **Settings → Actions → General** |
| No llega el aviso del resultado del CI/CD | Los cambios aún no están en `main`, o el nombre del workflow en la lista no coincide | Revisar `workflows:` en `telegram-release-ci.yml` |
| El aviso de un pull request falla | El pull request viene de un fork, que no tiene acceso a los secrets | Trabajar con ramas del mismo repositorio |

---

## Mantenimiento

- **Rotar el token:** en BotFather `/revoke`, y actualizar el secret `TELEGRAM_TOKEN`.
- **Cambiar de chat:** repetir los pasos 2 y 3, y actualizar el secret `TELEGRAM_CHAT_ID`.
- **Avisar el CI/CD de otro workflow:** agregar su nombre exacto a la lista `workflows:` de `telegram-release-ci.yml`.
- **Reducir el ruido del CI/CD:** agregar `branches: [main, develop]` bajo `workflow_run:` en `telegram-release-ci.yml` para avisar solo los resultados de esas ramas.
- **Cualquier cambio** a los workflows se sube con una rama y un Pull Request a `develop`, como indica la guía de [flujo de trabajo con Git](flujo-trabajo-git.md).
