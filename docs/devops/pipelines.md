
# Pipelines de GitHub Actions

## Objetivo

Este documento describe los 11 workflows de GitHub Actions de SignIA: qué hace cada uno, cuándo se ejecuta y por qué lo necesitamos. Los archivos están en `.github/workflows/`.

Las cifras de ejecuciones son del 16 de noviembre de 2026.

---

## Resumen

| Workflow                     | Tipo                   | Se ejecuta en                                    | Ejecuciones | Últimas 30             |
| ---------------------------- | ---------------------- | ------------------------------------------------ | ----------- | ----------------------- |
| `backend-ci.yml`           | CI                     | Push y pull request                              | 596         | 29 exitosas, 0 fallidas |
| `frontend-ci.yml`          | CI                     | Push y pull request que cambian `src/front/`   | 169         | 30 exitosas             |
| `docker-check.yml`         | CI                     | Push y pull request hacia `develop` o `main` | 124         | 28 exitosas, 0 fallidas |
| `SonarQube.yml`            | CI (calidad)           | Push a `main` y pull request                   | 110         | 28 exitosas, 1 fallida  |
| `backend-metrics.yml`      | CI (métricas)         | Push y pull request hacia `develop` o `main` | 107         | 30 exitosas             |
| `cd.yml`                   | CD                     | Tag `vX.Y.Z`                                   | 5           | 3 exitosas, 2 fallidas  |
| `close-issues-develop.yml` | Tablero (gestión)     | Pull request cerrado                             | 173         | 21 exitosas, 9 omitidas |
| `telegram-issues.yml`      | Tablero (integración) | Issue creada, cerrada o reabierta                | 68          | 30 exitosas             |
| `telegram-push-pr.yml`     | Notificación          | Push, pull request y revisión                   | 118         | 30 exitosas             |
| `telegram-release-ci.yml`  | Notificación          | Release y fin de CI                              | 96          | 30 exitosas             |
| `sms-twilio.yml`           | Notificación          | PR mergeado, release, fallo de CI y fin de CD    | 2           | 1 exitosa, 1 fallida    |

En la columna "Últimas 30", las ejecuciones que no aparecen como exitosas ni fallidas estaban en curso cuando se tomaron los datos. Las 9 omitidas de `close-issues-develop.yml` son pull requests que se cerraron sin mergear o que iban a una rama distinta de `develop`, donde el workflow no tiene nada que hacer.

---

## Integración continua (CI)

### `backend-ci.yml`: pruebas del backend

Levanta un PostgreSQL 16, carga el esquema, las migraciones y los datos iniciales, revisa el estilo con Ruff y corre las 435 pruebas del backend con `pytest`. Falla si una prueba falla o si la cobertura baja del 80 %. Guarda los reportes de cobertura y de resultados como artefacto.

Lo necesitamos porque cinco personas cambian el backend al mismo tiempo. Sin este workflow, un cambio que rompe una funcionalidad de otro integrante solo se notaría al probar la aplicación a mano. Con él, el error aparece en el mismo pull request y nadie lo mergea a `develop` sin verlo. También lo reutiliza el CD (`workflow_call`) para no publicar una versión con pruebas fallando.

### `frontend-ci.yml`: lint y build del frontend

Instala las dependencias con `npm ci`, corre ESLint y compila el frontend con `npm run build`. Solo se ejecuta cuando el cambio toca `src/front/`.

Un error de TypeScript o un import roto no se ve hasta que alguien compila. Este workflow asegura que lo que llega a `develop` compila, y al filtrar por la carpeta del frontend no gasta minutos de Actions en cambios que solo tocan el backend o la documentación.

### `docker-check.yml`: validación de Docker

Valida `docker-compose.yml`, construye las imágenes del backend y del frontend, levanta los contenedores y comprueba que el backend responda en `/health` y que el frontend cargue. Al final muestra los logs y apaga todo.

Como el sistema se despliega con Docker Compose, este workflow comprueba que las imágenes se siguen construyendo y que los servicios arrancan juntos después de cada cambio, antes de que el CD intente desplegarlos.

### `SonarQube.yml`: análisis de calidad

Corre las pruebas del backend, genera el reporte de cobertura y lo envía a SonarCloud junto con el código. SonarCloud aplica el Quality Gate y deja el resultado como check en el pull request.

SonarCloud revisa lo que las pruebas no miden: code smells, bugs, vulnerabilidades y duplicación, además de la cobertura. Con el check en cada pull request se ve si un cambio empeora la calidad antes de mergearlo. Los resultados están en [docs/calidad/metricas-calidad.md](../calidad/metricas-calidad.md).

### `backend-metrics.yml`: métricas propias

Calcula con Radon la complejidad ciclomática, el índice de mantenibilidad y las líneas de código, y con un script propio el acoplamiento entre módulos (Ce y Ca). Guarda los cuatro reportes como artefacto durante 30 días.

SonarCloud no calcula el índice de mantenibilidad ni el acoplamiento, así que estas métricas las medimos aparte. Con el workflow se recalculan solas en cada cambio y no dependen de que alguien las corra en su computador.

---

## Despliegue continuo (CD)

### `cd.yml`: publicación y despliegue

Se ejecuta al publicar un tag con formato `vX.Y.Z`. Tiene tres trabajos en orden:

1. **Pruebas:** reutiliza `backend-ci.yml`. Si fallan, no se publica nada.
2. **Publicación:** construye las imágenes del backend y del frontend y las sube a Docker Hub con dos etiquetas, la versión del tag y `latest`.
3. **Despliegue:** en un runner propio (`signia-wsl`) descarga las imágenes de esa versión, las levanta con Docker Compose, verifica que el backend y el frontend respondan y muestra los contenedores conectados a la red `signia_red`.

Con el CD cada versión queda publicada con un número que se puede volver a desplegar, y el despliegue se hace siempre con los mismos pasos en vez de depender de comandos a mano. Las dos ejecuciones fallidas fueron con los tags de prueba `v0.0.2-prueba` y `v0.0.3-prueba`, mientras se ajustaba el workflow; desde `v0.0.4-prueba` hasta `v1.0.0` el CD termina bien. El detalle está en [docs/cd/pipeline_cd.md](../cd/pipeline_cd.md).

---

## Automatización del tablero (kanban)

### `close-issues-develop.yml`: gestión de issues

Cuando se mergea un pull request en `develop`, lee la descripción del PR, busca referencias como `Closes #N`, `Fixes #N` o `Resolves #N` y cierra esas issues.

GitHub solo cierra issues de forma automática cuando el pull request entra a la rama por defecto (`main`). Como nosotros integramos en `develop`, las tareas se quedaban abiertas en el tablero aunque ya estuvieran terminadas. Con este workflow la issue se cierra en cuanto su trabajo entra a `develop`, y el tablero de GitHub Projects muestra el estado real del sprint sin que nadie tenga que moverla a mano.

### `telegram-issues.yml`: integración del tablero con Telegram

Cada vez que se crea, se cierra o se reabre una issue, manda un mensaje al chat del equipo en Telegram con el título, el número, el autor y el enlace.

En las retrospectivas la comunicación apareció varias veces como lo que había que mejorar, y en el Sprint 5 hubo trabajo duplicado en una misma HU. Con este aviso todo el equipo se entera en el momento de las tareas nuevas y de las que se cierran, sin tener que entrar al tablero. El detalle está en [docs/NotificacionesTelegram.md](../NotificacionesTelegram.md).

---

## Notificaciones

### `telegram-push-pr.yml`

Avisa en Telegram de cada push (rama, autor y commits), de los pull requests que se abren, se mergean o se cierran, y de las revisiones (aprobado, cambios pedidos o comentario).

Los pull requests necesitan una aprobación para mergearse, y este aviso hace que el revisor se entere apenas lo asignan y que el autor sepa cuándo le aprobaron o le pidieron cambios.

### `telegram-release-ci.yml`

Avisa en Telegram cuando se publica un release y cuando termina Backend CI, Frontend CI o SonarQube, con el resultado y el enlace a la ejecución.

Si el CI falla en `develop`, alguien tiene que arreglarlo antes de que otros integrantes construyan encima. El aviso con el enlace directo a la ejecución reduce el tiempo hasta que alguien lo revisa.

### `sms-twilio.yml`

Manda un SMS al celular del equipo con la API de Twilio cuando se mergea un pull request en `develop` o `main`, se publica un release, falla Backend CI, SonarQube o el CD, o termina el CD.

Es la integración del proyecto con un proveedor de SMS. Llega aunque alguien no esté pendiente de Telegram, y solo se usa para estos eventos porque cada SMS gasta saldo. La ejecución fallida fue la primera: la cuenta de prueba de Twilio solo acepta plantillas predefinidas y se corrigió en el pull request siguiente. El detalle está en [docs/NotificacionesSMS.md](../NotificacionesSMS.md).

---

## Cómo trabajan juntos

```text
Pull request hacia develop
  ├─ backend-ci, frontend-ci, docker-check, SonarQube y backend-metrics revisan el cambio
  ├─ telegram-push-pr avisa al revisor
  └─ al mergear:
       ├─ close-issues-develop cierra las issues referenciadas
       ├─ telegram-issues avisa del cierre
       └─ sms-twilio avisa del merge

Tag vX.Y.Z
  └─ cd: pruebas → publicación en Docker Hub → despliegue con Docker Compose
       └─ telegram-release-ci y sms-twilio avisan del resultado
```
