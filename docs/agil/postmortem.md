# Postmortem de SignIA

## Objetivo

Este documento revisa cómo nos fue con SignIA desde el 10 de agosto hasta el 16 de noviembre de 2026, tanto en lo técnico como en la forma de trabajar. Para cada problema buscamos la causa raíz y dejamos una acción concreta para no repetirlo.

Las fuentes son las retrospectivas de los sprints (issues #14 a #528 y sus comentarios), los Sprint Planning y Review, el historial de Git y los pull requests. Los números del proyecto están en el [reporte de metodología ágil](reporte-agil.md).

---

## Resumen del proyecto

SignIA es una plataforma web para aprender el alfabeto de la Lengua de Señas Colombiana (LSC) y practicarlo con la cámara. El usuario consulta cada letra, practica frente a la cámara, el sistema reconoce la seña con MediaPipe y guarda los intentos, los aciertos y el progreso.

| Dato                    | Valor                                                                              |
| ----------------------- | ---------------------------------------------------------------------------------- |
| Duración               | 14 sprints de una semana (10 de agosto al 16 de noviembre de 2026)                 |
| Historias de usuario    | 55 cerradas de 56                                                                  |
| Pull requests mergeados | 218                                                                                |
| Entregas                | Semana 7, semana 12 y semana 16 (sustentación final el 17 de noviembre)           |
| Stack                   | React + TypeScript, FastAPI, PostgreSQL, MediaPipe, Docker Compose, GitHub Actions |

---

## Qué salió bien

### En lo técnico

- El flujo principal funciona de punta a punta. Registro, inicio de sesión, módulo Aprender, práctica con cámara, reconocimiento de letras estáticas y con movimiento, registro de intentos, letras aprendidas por número de aciertos e historial.
- Automatizamos casi todo el ciclo de desarrollo. Al final quedaron workflows de CI para backend y frontend, validación de Docker, análisis con SonarQube, métricas de código, CD con publicación en Docker Hub y despliegue con Docker Compose, cierre automático de issues y avisos por Telegram y SMS.
- Las pruebas del backend tienen un mínimo de cobertura obligatorio. El workflow de Backend CI falla si la cobertura baja del 80 % (`--cov-fail-under=80`).
- Aplicamos patrones de diseño: Observer, Facade y Factory Method en la práctica (Entrega 2), y Facade en la recuperación de contraseña y Chain of Responsibility en la autenticación (entrega final).

### En el proceso

- Registramos las ceremonias en GitHub con plantillas propias: 14 Sprint Planning, 37 Daily, 10 Sprint Review y 12 Sprint Retrospective.
- Los cambios pasaron por pull request con revisión. De 185 revisiones, 182 fueron aprobaciones, y `main` solo recibe cambios desde `develop`.
- Las retrospectivas mejoraron con el tiempo. Las primeras tenían respuestas cortas ("todo", "nada"). Desde el Sprint 11 cada retrospectiva trae el resultado del sprint, el formato comenzar / más de / seguir / menos de / dejar de hacer y una tabla de acciones con responsable. Además, las acciones se revisaban en el sprint siguiente: en la retrospectiva del Sprint 12 aparece cumplida la acción 3 del Sprint 11 (revisar el código antes de diagramar).

---

## Qué salió mal

### En el proceso

| #  | Problema                                   | Evidencia                                                                                                                                                                                                            |
| -- | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| P1 | Dos sprints casi sin resultados            | Sprint 9: la retrospectiva dice "no se pudo realizar casi nada" (1 HU cerrada, 16 commits). Sprint 11: no se completó ninguna tarea de la HU #44 y el Sprint Goal no se cumplió.                                   |
| P2 | Una HU se arrastró cuatro sprints         | La HU #44 (#479, diagramas en Visual Paradigm) empezó en el Sprint 11 y se cerró en el 14. La sub-issue #498 pasó de sprint en sprint sin responsable.                                                            |
| P3 | Trabajo duplicado y falta de comunicación | En la retrospectiva del Sprint 5 se habla de "duplicaciones de trabajo para una misma HU ya implementada". La comunicación aparece como lo que hay que mejorar en las retrospectivas de los sprints 1, 2, 5, 6 y 8. |
| P4 | Participación desigual al principio       | En las retrospectivas de los sprints 3 y 4 se pide repartir mejor el trabajo y las contribuciones de cada persona. En los sprints 1 a 3 algunos integrantes tienen 1 o 2 commits por sprint.                         |
| P5 | Trazabilidad incompleta                    | 25 de las 56 HU no tienen milestone. Hay números de HU repetidos (dos HU #15) y en el Sprint Backlog del Sprint 13 se escribió "#44", que GitHub enlazó a otro issue.                                             |
| P6 | Retrospectivas con poco análisis          | No hay retrospectiva de los sprints 10 y 14, y la del Sprint 2 (#48) quedó titulada como "Sprint Retrospective 1". Hasta el Sprint 9 muchas respuestas son "todo" o "nada", sin decir qué pasó ni por qué.       |
| P7 | Tareas para el último día                | Lo dicen las retrospectivas de los sprints 5, 6 y 11 ("hacer las tareas en tiempo", "dejar las tareas para el último día").                                                                                        |

### En lo técnico

| #  | Problema                                               | Evidencia                                                                                                                                                                                                                                                                         |
| -- | ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| T1 | Diagramas rehechos                                     | El profesor pidió corregir el diagrama de contenedores (tenía el navegador y la cámara como contenedores) y el de componentes (mostraba pasos de un flujo y no componentes). El diagrama del patrón Observer se empezó como C4 y hubo que rehacerlo como diagrama de clases. |
| T2 | Calidad y despliegue automatizados muy tarde           | SonarQube llegó el 29 de octubre, las métricas el 10 de noviembre y el CD el 13 de noviembre, en las últimas tres semanas del proyecto.                                                                                                                                        |
| T3 | Endpoint de recuperación de contraseña sin registrar | Las rutas de recuperación existen y tienen pruebas, pero `app/main.py` no las incluye, así que en la aplicación real responden 404. Las pruebas no lo detectaron porque cada una monta su propia aplicación con el router.                                                  |
| T4 | Límite de Twilio descubierto en el primer envío real | La cuenta de prueba solo acepta plantillas predefinidas. El primer SMS automático falló con HTTP 400 y hubo que cambiar el workflow para enviar el nombre de la plantilla. |
| T5 | El despliegue depende de un runner local | El job de despliegue corre en un runner self-hosted en WSL: si ese equipo está apagado, el job queda en cola. Además, el tag `v1` no siguió el patrón `v*.*.*`, así que el CD no se ejecutó y no se publicaron imágenes. |

---

## Causas raíz

| Problemas  | Causa raíz                                                                                                                                                                                                                                                                                                                                                           |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| P1, P2, P7 | Las HU grandes no se partían en tareas de un día y varias sub-issues quedaban sin responsable desde el Sprint Planning. Las tareas pequeñas, como la validación #498, quedaban sin dueño y los bloqueos se veían el último día, cuando ya no había tiempo. En el Sprint 11 además se comprometió más trabajo del que cabía en un sprint de cuatro días. |
| P3, P4     | Al principio no había una regla para tomar tareas: nadie revisaba el tablero antes de empezar algo ni avisaba en el grupo, y así dos personas terminaron trabajando en la misma HU. El reparto de tareas tampoco se revisaba sprint a sprint, hasta que se señaló en las retrospectivas de los sprints 3 y 4.                                                     |
| P5         | Crear la HU, ponerle milestone y enlazarla era un paso manual que dependía de quien la creara, y nadie lo revisaba.                                                                                                                                                                                                                                                  |
| P6         | La plantilla de retrospectiva solo tenía tres preguntas abiertas y no pedía datos del sprint, así que era fácil contestar "todo bien".                                                                                                                                                                                                                            |
| T1         | Empezamos a diagramar sin acordar el tipo de diagrama ni la notación, y sin contrastar antes con el código real del backend.                                                                                                                                                                                                                                        |
| T2         | Montamos la automatización cuando las funcionalidades ya estaban construidas. SonarQube, las métricas y el CD llegaron en las últimas tres semanas, cuando ya no había tiempo de corregir con calma lo que encontraban.                                                                                                                                           |
| T3         | Solo había pruebas unitarias de cada ruta. No había una prueba que revisara qué rutas expone la aplicación completa (`app.main`).                                                                                                                                                                                                                               |
| T4         | No leímos las condiciones de la cuenta de prueba antes de integrar. La prueba manual desde la consola de Twilio funcionó porque la consola usa plantillas por defecto.                                                                                        

| T5         | No teníamos un servidor propio para desplegar, así que el despliegue quedó atado al equipo de un integrante. La convención de versiones (`vX.Y.Z`) no estaba escrita antes de crear el primer tag, y el workflow solo se activa con ese formato. |

---

## Acciones de mejora

| Prioridad | Acción                                                                                                                                     | Cómo corrige el problema                                                              | Problemas  | Responsable                  |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | ---------- | ---------------------------- |
| 1         | Partir cada HU en sub-issues de máximo un día y asignar responsable y fecha a todas en el Sprint Planning                                 | Ninguna tarea queda sin dueño y el avance se ve día a día                           | P1, P2, P7 | Sprint Planner               |
| 2         | Hacer un chequeo de avance a mitad de cada sprint con el tablero de GitHub Projects                                                         | Los bloqueos aparecen cuando todavía hay tiempo de mover tareas o reducir el alcance  | P1, P2     | Scrum Master                 |
| 3         | Antes de empezar una tarea, moverla a "In progress" en el tablero y avisar en el grupo                                                      | Evita que dos personas trabajen en la misma HU y deja claro qué tiene cada uno        | P3, P4     | Todo el equipo               |
| 4         | Crear los workflows de CI, Docker y SonarQube en el primer sprint de desarrollo                                                             | Los errores de entorno y de calidad aparecen en el mismo PR que los causa              | T2         | DevOps Engineer              |
| 5         | Agregar una prueba sobre `app.main` que revise que todas las rutas documentadas existen                                                   | Detecta un router sin registrar, como el de recuperación de contraseña               | T3         | QA Lead                      |
| 6         | Escribir en cada sub-issue de diagrama el tipo y la notación, y revisar el código antes de dibujar                                        | Se evita rehacer diagramas por notación o por no reflejar el sistema real             | T1         | Encargado de la HU           |
| 7         | Usar una plantilla de retrospectiva con resultado del sprint y tabla de acciones (la de los sprints 11 a 13) y hacerla en todos los sprints | Cada retrospectiva deja causas y acciones que se pueden revisar en el sprint siguiente | P6         | Scrum Master                 |
| 8         | Revisar al crear cada HU que tenga milestone, labels y que su número sea único                                                            | La trazabilidad queda completa desde el inicio                                         | P5         | Product Owner                |
| 9         | Leer los límites del plan o la cuenta de prueba antes de integrar un servicio externo                                                      | Se evitan sorpresas como la de las plantillas de Twilio                                | T4         | Encargado de la integración |
| 10        | Documentar la convención de tags `vX.Y.Z` en el README y, a futuro, desplegar en un servidor o servicio en la nube | Cualquier integrante crea tags que activan el CD, y el despliegue no depende de que un equipo esté encendido | T5         | DevOps Engineer              |
---

## Retrospectiva estrella

Resumen del postmortem en las cinco categorías que usamos en las retrospectivas del equipo.

<img width="1920" height="1200" alt="Subtítulo" src="https://github.com/user-attachments/assets/e0deff19-0925-48e7-aa2c-6fa3a9b73f47" />

## Lecciones aprendidas

- Cuando una tarea tenía responsable y fecha se cerraba en el sprint. Las que no tenían responsable, como #498, pasaron de un sprint a otro.
- El CI de backend lo tuvimos desde el Sprint 6 y nos avisó de pruebas rotas en el momento. SonarQube, las métricas y el CD llegaron en las últimas tres semanas, cuando quedaba poco tiempo para corregir lo que encontraban.
- Las pruebas de la recuperación de contraseña pasan, pero la ruta no existe en la aplicación real. Además de probar cada ruta por separado, hay que probar la aplicación completa.
- Las retrospectivas sirven cuando se escriben con datos y acciones concretas. Las de los sprints 11 a 13 fueron las primeras que dejaron acciones con responsable, y en la del Sprint 12 ya aparece cumplida una de las acciones del Sprint 11.
