
# Plan de pruebas

## Objetivo

Este documento explica cómo probamos el backend de SignIA: qué tipos de pruebas hay, qué componentes cubren, cómo se ejecutan en GitHub Actions y qué dicen los resultados de cobertura en SonarCloud.

Los datos de cobertura son del último análisis de la rama `main` en SonarCloud (12 de noviembre de 2026).

---

## Resumen

| Dato                                | Valor                                             |
| ----------------------------------- | ------------------------------------------------- |
| Archivos de prueba del backend      | 53 (en `src/tests/`)                            |
| Pruebas del backend                 | 435                                               |
| Cobertura del backend en SonarCloud | 85,2 % (1.490 de 1.748 líneas cubiertas)         |
| Cobertura mínima exigida por el CI | 80 %                                              |
| Quality Gate de SonarCloud          | Aprobado                                          |
| Pruebas del frontend                | 1 archivo (`src/front/tests/Aprender.test.tsx`) |

---

## Herramientas

| Herramienta                       | Uso                                                    |
| --------------------------------- | ------------------------------------------------------ |
| `unittest`                      | Escribir las pruebas del backend                       |
| `pytest` y `pytest-cov`       | Ejecutar las pruebas y medir la cobertura              |
| `fastapi.testclient.TestClient` | Probar las rutas de la API sin levantar el servidor    |
| PostgreSQL 16                     | Base de datos de las pruebas de integración en el CI  |
| SonarCloud                        | Publicar la cobertura y revisar la calidad del código |
| Vitest y React Testing Library    | Pruebas del frontend                                   |

---

## Tipos de pruebas

| Tipo                             | Archivos | Pruebas | Qué validan                                                                                                                                                                                                                                                                          |
| -------------------------------- | -------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Unitarias de servicios y lógica | 21       | 192     | Reglas de negocio de cada servicio con la base de datos y los servicios externos simulados (`unittest.mock`): aprendizaje por aciertos, cálculo de progreso, recuperación de contraseña, estrategias y decoradores del reconocimiento, patrones Facade y Chain of Responsibility |
| De rutas de la API               | 18       | 183     | Cada endpoint con `TestClient`: códigos HTTP, validación de datos de entrada, autenticación con JWT, permisos de administrador y mensajes de error                                                                                                                               |
| De integración con PostgreSQL   | 14       | 60      | Flujos completos contra una base de datos real: crear una sesión, registrar resultados e intentos, actualizar el progreso y consultar el historial                                                                                                                                   |

Los archivos de integración terminan en `_integracion.py` y usan `@unittest.skipUnless(os.getenv("DATABASE_URL"))`. Si la variable no existe, se omiten. Así cada integrante puede correr las pruebas unitarias sin tener una base de datos, y en el CI corren todas.

---

## Componentes cubiertos

| Componente                                        | Pruebas | Archivos principales                                                                                                                         | Cobertura en SonarCloud                                                                                |
| ------------------------------------------------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Autenticación, usuarios y perfil                 | 69      | `test_autenticacion.py`, `test_cadena_autenticacion.py`, `test_usuarios.py`, `test_perfil.py`                                        | `cadena_autenticacion.py` 98,2 %, `routes/usuarios.py` 79,3 %, `autenticacion_service.py` 61,1 % |
| Recuperación y restablecimiento de contraseña   | 106     | `test_recuperacion_service.py`, `test_correo_recuperacion.py`, `test_fachada_recuperacion_contrasena.py`, `test_restablecimiento.py` | `correo_recuperacion_service.py` 99 %, `restablecimiento_service.py` 96 %                          |
| Sesiones, resultados e intentos de reconocimiento | 103     | `test_sesiones_*.py`, `test_resultados_*.py`, `test_intentos_*.py`, `test_endpoint_resultados_integracion.py`                        | `routes/sesiones.py` 97,3 %, `resultados_reconocimiento_service.py` 86,1 %                         |
| Progreso, aprendizaje e historial                 | 76      | `test_aprendizaje_service.py`, `test_progreso_*.py`, `test_historial_*.py`, `test_porcentaje_progreso_integracion.py`                | `progreso_service.py` 83,3 %                                                                         |
| Visión por computador                            | 52      | `test_vision_service.py`, `test_casos_borde_reconocimiento.py`, `test_estrategias_reconocimiento.py`, `test_gestor_detectores.py`    | `vision_service.py` 96,1 %, `gestor_detectores.py` 93,9 %                                          |
| Letras del alfabeto                               | 29      | `test_letras.py`, `test_letras_service.py`, `test_estado_letras*.py`                                                                   | Incluida en `app/services` y `app/routes`                                                          |

Cobertura por carpeta:

| Carpeta                 | Líneas a cubrir | Sin cubrir    | Cobertura        |
| ----------------------- | ---------------- | ------------- | ---------------- |
| `app/repositories`    | 7                | 0             | 100 %            |
| `app/services`        | 716              | 34            | 95,3 %           |
| `app/routes`          | 409              | 25            | 93,9 %           |
| `app/vision`          | 502              | 193           | 61,6 %           |
| **Total `app`** | **1.748**  | **258** | **85,2 %** |

---

## Ejecución automática

Las pruebas se ejecutan automáticamente en dos workflows:

| Workflow           | Cuándo se ejecuta                                              | Qué hace con las pruebas                                                                                                                                                                                            |
| ------------------ | --------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `backend-ci.yml` | En cada push a cualquier rama y en cada pull request            | Levanta PostgreSQL 16, carga `schema.sql`, las migraciones y `seed.sql`, corre Ruff y luego `pytest` con `--cov-fail-under=80`. Si la cobertura baja del 80 % o falla una prueba, el workflow queda en rojo. |
| `SonarQube.yml`  | En cada push a `main` y al abrir o actualizar un pull request | Vuelve a correr las pruebas, genera `reports/cobertura.xml` y lo envía a SonarCloud, que aplica el Quality Gate y deja el resultado como check en el pull request.                                                |

`backend-ci.yml` guarda como artefacto `reportes-pruebas-backend` tres reportes: la cobertura en XML (`reports/cobertura.xml`), la cobertura en HTML (`reports/cobertura_html`) y el resultado de las pruebas en formato JUnit (`reports/resultados.xml`). Se descargan desde la ejecución en la pestaña Actions.

El CI y SonarCloud usan el mismo comando de cobertura sobre la carpeta `app`, por eso el porcentaje que muestra el reporte del CI coincide con el de SonarCloud.

---

## Cómo correr las pruebas en local

Desde la raíz del proyecto, con las dependencias instaladas:

```bash
python -m pytest src/tests -q
```

Con cobertura:

```bash
python -m pytest src/tests --cov=app --cov-report=term-missing
```

Para incluir las pruebas de integración hay que definir `DATABASE_URL` con una base de datos de pruebas que tenga el esquema y las migraciones cargadas. No se debe usar la base de datos de producción, porque estas pruebas escriben datos.

Frontend, desde `src/front/`:

```bash
npm test
npm run test:coverage
```

---

## Interpretación de los resultados

Un 85,2 % de cobertura quiere decir que las pruebas ejecutan 1.490 de las 1.748 líneas del backend. Está por encima del 80 % que exige el CI y el Quality Gate de SonarCloud está aprobado, sin bugs ni vulnerabilidades reportados.

La cobertura no es pareja entre carpetas. Los servicios (95,3 %) y las rutas (93,9 %), que son los que leen y guardan los datos del usuario, están casi completos. La carpeta `app/vision` baja al 61,6 % por dos razones:

- `app/vision/prototype/main.py` tiene 0 % y aporta 104 de las 258 líneas sin cubrir del proyecto. Es el prototipo inicial que abre la cámara en una ventana con OpenCV y no lo usa la API.
- `letras_movimiento.py` (22,6 %), `movimientos.py` (44,4 %) y `detector.py` (40 %) dependen de MediaPipe y de imágenes reales de la cámara, que son más difíciles de simular en una prueba.

