# Reporte de metodología ágil

## Objetivo

Este reporte resume cómo aplicamos Scrum en SignIA entre el 10 de agosto y el 16 de noviembre de 2026: los milestones, los sprints, las historias de usuario cerradas, los commits y la participación de cada integrante. Todos los datos salen del repositorio y de GitHub (issues, pull requests, revisiones y el historial de Git) con corte al 16 de noviembre de 2026.

No se cuentan los commits ni los pull requests de los monitores del curso, porque no hacen parte del equipo.

---

## Equipo y roles

| Integrante | Rol en Scrum | Usuario de GitHub |
|---|---|---|
| Isabel Gutiérrez | Scrum Master | `Isabelsgp` |
| Juan Diego Arévalo | Product Owner y QA Lead | `Juan123839` |
| Juan Pablo Vanegas | Sprint Planner | `juanpvanegasvelandia02-ship-it` |
| David Vallejo | Configuration Manager | `David-wallpaper` |
| Óscar Martínez Mantilla | DevOps Engineer | `martinezm-oe` |

---

## Cómo trabajamos

Trabajamos en sprints de una semana. Cada ceremonia de Scrum quedó registrada como un issue en el repositorio, con las plantillas de `.github/ISSUE_TEMPLATE/` (`sprint-planning.yml`, `daily.yml`, `user-story.yml` y `sub-issue.yml`):

| Ceremonia | Issues registrados |
|---|---|
| Sprint Planning | 14 |
| Daily Scrum | 37 |
| Sprint Review | 10 |
| Sprint Retrospective | 10 |

Cada Sprint Planning tiene la duración del sprint, el Sprint Goal, el Sprint Backlog, los entregables y los criterios de aceptación. Las historias de usuario se escriben con la plantilla de HU y se dividen en sub-issues (tasks) que se asignan a un integrante. El seguimiento se hace en el tablero del proyecto `FIS_2630_1204_G4` en GitHub Projects.

Las entregas del curso fueron en la semana 7 (Entrega 1), la semana 12 (Entrega 2) y la semana 16 (Entrega 3, sustentación final el martes 17 de noviembre de 2026).

---

## Milestones

| Milestone | Objetivo | Issues | HU | Issues abiertas | Avance |
|---|---|---|---|---|---|
| M0 - Planeación y Base del Proyecto | Repositorio, historias de usuario, Product Backlog, arquitectura inicial y documentación base | 28 | 5 | 0 | 100 % |
| M1 - Base Multiusuario de SignIA | Base funcional multiusuario con frontend, backend y base de datos integrados | 21 | 4 | 0 | 100 % |
| M2 - Módulo de Aprendizaje y Contenido LSC | Consultar y aprender las letras del alfabeto LSC con imágenes, descripciones y navegación a la práctica | 61 | 15 | 0 | 100 % |
| M3 - Reconocimiento y Práctica de Señas | Flujo principal de reconocimiento y práctica, presentado en la Entrega 2 | 43 | 7 | 0 | 100 % |

Los cuatro milestones tienen todos sus issues cerrados.

---

## Sprints

| Sprint | Fechas | Sprint Goal |
|---|---|---|
| 1 | 10 al 14 de agosto | Crear y organizar el repositorio para trabajar con Scrum (labels, README, wiki) |
| 2 | 17 al 22 de agosto | Taller 1: actores, roles, historias de usuario, criterios de aceptación y mockups |
| 3 | 24 al 30 de agosto | Base funcional: integración inicial de frontend, backend y PostgreSQL, registro e inicio de sesión |
| 4 | 31 de agosto al 7 de septiembre | Primera versión con autenticación, cámara activa y detección de la mano con MediaPipe |
| 5 | 7 al 14 de septiembre | Integrar el reconocimiento de señas con la plataforma y guardar sesiones y resultados |
| 6 | 14 al 21 de septiembre | Reconocimiento de vocales conectado al aprendizaje y registro del progreso |
| 7 | 21 al 28 de septiembre | Completar la experiencia de aprendizaje: nuevas letras, estado de aprendizaje y progreso |
| 8 | 28 de septiembre al 5 de octubre | Mejorar la precisión del reconocimiento y registrar aciertos e intentos automáticamente |
| 9 | 5 al 12 de octubre | Consolidación técnica para la Entrega 2: arquitectura, patrón GoF, pruebas y GitHub Actions |
| 10 | 12 al 19 de octubre | Cerrar lo pendiente del Sprint 9 y dejar listo el sistema para la Entrega 2 |
| 11 | 20 al 23 de octubre | Corregir los diagramas de arquitectura y de dominio según las observaciones del profesor |
| 12 | 27 al 30 de octubre | Terminar los diagramas pendientes y revisar calidad y rendimiento con SonarQube y JMeter |
| 13 | 3 al 6 de noviembre | Cerrar la HU #44 (diagramas en Visual Paradigm) y el diagrama del patrón Facade |
| 14 | 9 al 13 de noviembre | Preparar la Entrega 3: producto final, CI/CD, notificaciones, reporte ágil, postmortem y pitch |

Para contar issues, pull requests y commits por sprint, los días que quedan entre un sprint y el siguiente se suman al sprint anterior. Los días del 14 al 16 de noviembre cuentan dentro del Sprint 14.

El Sprint 11 no tiene commits porque se dedicó a corregir los diagramas en Visual Paradigm, que no están en el repositorio.

---

## Historias de usuario por sprint

En total hay 56 historias de usuario: 55 cerradas y 1 abierta (#564, instalar y entender SignIA sin depender del equipo).

| Sprint | HU cerradas | Issues cerrados (HU, tasks y ceremonias) | HU que se cerraron |
|---|---|---|---|
| 1 | 0 | 0 | |
| 2 | 0 | 12 | |
| 3 | 0 | 20 | |
| 4 | 12 | 47 | #25, #28, #29, #33, #70, #71, #101, #109, #122, #123, #124, #133 |
| 5 | 8 | 46 | #24, #125, #142, #148, #152, #163, #173, #198 |
| 6 | 6 | 33 | #228, #234, #241, #253, #257, #267 |
| 7 | 6 | 39 | #243, #289, #296, #303, #310, #320 |
| 8 | 7 | 46 | #316, #359, #365, #370, #378, #383, #390 |
| 9 | 1 | 8 | #426 |
| 10 | 1 | 6 | #421 |
| 11 | 0 | 10 | |
| 12 | 2 | 21 | #31, #430 |
| 13 | 0 | 7 | |
| 14 | 12 | 66 | #479, #531, #535, #540, #547, #554, #559, #569, #582, #592, #606, #615 |
| **Total** | **55** | **361** | |

En promedio se cerraron 3,9 HU por sprint (55 HU en 14 sprints) y 25,8 issues por sprint.

Los sprints 1 a 3 no cierran HU porque se usaron para organizar el repositorio, escribir las historias de usuario y montar la base del proyecto; las primeras HU se cierran en el Sprint 4. Los sprints 9 a 13 cierran menos HU porque el trabajo fue de arquitectura, diagramas, pruebas y automatización, que se registró como tasks y sub-issues. La HU #44 (#479), por ejemplo, tuvo 13 sub-issues y se trabajó desde el Sprint 11 hasta el 14.

---

## Commits por sprint

Los commits se cuentan en todas las ramas, sin contar los commits de merge.

| Sprint | David | Juan Diego | Óscar | Isabel | Juan Pablo | Total |
|---|---|---|---|---|---|---|
| 1 | 4 | 0 | 1 | 4 | 1 | 10 |
| 2 | 9 | 14 | 1 | 9 | 4 | 37 |
| 3 | 16 | 15 | 1 | 2 | 2 | 36 |
| 4 | 28 | 8 | 9 | 8 | 4 | 57 |
| 5 | 77 | 4 | 9 | 10 | 5 | 105 |
| 6 | 26 | 20 | 40 | 10 | 4 | 100 |
| 7 | 37 | 26 | 27 | 10 | 21 | 121 |
| 8 | 31 | 6 | 30 | 10 | 23 | 100 |
| 9 | 8 | 2 | 0 | 0 | 6 | 16 |
| 10 | 4 | 6 | 1 | 6 | 4 | 21 |
| 11 | 0 | 0 | 0 | 0 | 0 | 0 |
| 12 | 19 | 2 | 0 | 0 | 0 | 21 |
| 13 | 1 | 1 | 0 | 0 | 5 | 7 |
| 14 | 35 | 17 | 12 | 11 | 4 | 79 |
| **Total** | **295** | **121** | **131** | **80** | **83** | **710** |

En promedio hubo 50,7 commits por sprint y 142 commits por integrante en todo el proyecto.

---

## Participación del equipo

| Integrante | Commits | Sprints con commits (de 14) | HU asignadas | Issues cerrados asignados | PR mergeados | Revisiones de PR |
|---|---|---|---|---|---|---|
| David | 295 | 13 | 22 | 127 | 111 | 77 |
| Juan Diego | 121 | 12 | 21 | 111 | 46 | 100 |
| Óscar | 131 | 10 | 12 | 57 | 19 | 3 |
| Isabel | 80 | 10 | 12 | 64 | 14 | 4 |
| Juan Pablo | 83 | 12 | 13 | 78 | 28 | 1 |

En total se mergearon 218 pull requests y se hicieron 185 revisiones, 182 de ellas aprobaciones.

Repartimos el trabajo por funcionalidades: cada integrante tuvo historias de usuario propias y sus sub-issues, y los cinco tuvieron commits en al menos 10 de los 14 sprints. Que unos tengan más commits que otros depende sobre todo de la forma de trabajar de cada uno, porque hay quienes hacen commits pequeños y seguidos y quienes agrupan más cambios en cada commit. La mediana de líneas cambiadas por commit (contando solo código y documentación) lo muestra: Óscar tiene 10 y Juan Pablo 19, mientras que David, Juan Diego e Isabel están entre 48 y 55.

Los roles también explican parte de la diferencia. David, como Configuration Manager, abrió 111 de los 218 pull requests, muchos de ellos de integración hacia `develop` y `main`. Juan Diego, como Product Owner y QA Lead, hizo la mayoría de las revisiones. Isabel, como Scrum Master, registró 42 de los 71 issues de ceremonias (plannings, dailies, reviews y retrospectivas), un trabajo que no genera commits.

---

## Control de versiones

El flujo de ramas está descrito en [docs/flujo-trabajo-git.md](../flujo-trabajo-git.md):

```text
rama individual o de tarea → develop → main
```

- `main` tiene la versión estable, está protegida y solo recibe cambios por pull request desde `develop`.
- `develop` integra el trabajo del equipo.
- Cada integrante tiene su rama (`feature-DavidV`, `feature-Diego`, `feature-Isabel`, `feature-JuanVanegas`, `feature-OscarM&M`) y para tareas puntuales se usan ramas `feature/`, `fix/`, `docs/`, `test/` y `chore/`.
- Los cambios entran por pull request con al menos una aprobación. De los 218 pull requests mergeados, 142 fueron hacia `develop`, 62 hacia `main` y 14 hacia ramas individuales.
- La mayoría de los commits usan Gitmoji y el formato `tipo(alcance): descripción #issue`.

Las versiones se marcan con tags `vX.Y.Z`. El tag `v1.0.0` (14 de noviembre de 2026) dispara el pipeline de CD, que publica las imágenes en Docker Hub con esa versión y las despliega con Docker Compose (ver [docs/cd/pipeline_cd.md](../cd/pipeline_cd.md)).

---

## Trazabilidad

Cada cambio se puede seguir desde la historia de usuario hasta la versión:

1. La HU se crea como issue con la plantilla y se divide en sub-issues.
2. Se crea una rama para la tarea.
3. Los commits mencionan el número del issue (`#N`).
4. El pull request enlaza el issue con `Closes #N`.
5. Al mergear en `develop`, el workflow `close-issues-develop.yml` cierra el issue.
6. La versión que lo incluye se publica con un tag.

Ejemplo con la HU de notificaciones por SMS:

| Paso | Dónde |
|---|---|
| HU | #615 Notificar al equipo por SMS los eventos críticos del proyecto |
| Rama | `feature/sms-twilio` |
| Commits | `✨ feat(sms): agregar workflow de avisos por SMS con Twilio #615` y `📝 docs(sms): documentar la integración de SMS con Twilio #615` |
| Pull request | #616, aprobado por David y mergeado en `develop` |
| Cierre | `github-actions[bot]` cerró el issue #615 al mergear el PR |

---

## Pendientes

- La HU #564 (instalar y entender SignIA sin depender del equipo) sigue abierta, junto con las tasks #558 (release final), #563 (postmortem), #566 (README) y #567 (wiki).
- 25 de las 56 HU no tienen milestone asignado en GitHub, aunque sí están en un Sprint Planning.
- Los cuatro milestones tienen el 100 % de sus issues cerrados, pero en GitHub siguen marcados como abiertos.