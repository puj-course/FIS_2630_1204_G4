
# Métricas de calidad

## Objetivo

Este documento explica las métricas de calidad que medimos en el backend de SignIA: qué mide cada una, qué resultado dio, qué significa ese resultado para el sistema y qué haríamos para mejorar lo que salió por debajo de lo esperado.

Medimos la calidad de dos formas:

- Métricas propias en el código, calculadas en el workflow `backend-metrics.yml` con Radon y con un script de acoplamiento escrito por nosotros. SonarQube no calcula el índice de mantenibilidad ni el acoplamiento entre módulos, y la complejidad la reporta como un total del proyecto y como complejidad cognitiva, no función por función con la escala de A a F que usa Radon.
- Métricas de SonarQube, calculadas por SonarCloud en el workflow `SonarQube.yml`.

Los valores de Radon y del acoplamiento son de la rama `develop` al 16 de noviembre de 2026. Los de SonarCloud son del último análisis de `main` (12 de noviembre de 2026).

---

## Resumen

| Métrica                         | Herramienta             | Resultado                                                    | Lectura                              |
| -------------------------------- | ----------------------- | ------------------------------------------------------------ | ------------------------------------ |
| Complejidad ciclomática         | Radon (`radon cc`)    | Promedio A (2,5) en 221 funciones y clases; 2 funciones en C | Bien, con dos funciones para dividir |
| Índice de mantenibilidad        | Radon (`radon mi`)    | 52 de 52 archivos en A; promedio 77,0                        | Bien                                 |
| Líneas de código y comentarios | Radon (`radon raw`)   | 4.571 líneas de código; 7 % de comentarios y docstrings    | Pocos comentarios                    |
| Acoplamiento entre módulos      | Script propio (Ce / Ca) | 53 módulos, 89 dependencias internas, Ce promedio 1,68      | Bajo, con dos módulos muy usados    |
| Cobertura de pruebas             | SonarCloud              | 85,2 %                                                       | Por encima del 80 % exigido          |
| Mantenibilidad                   | SonarCloud              | A; 34 code smells menores; deuda técnica de 67 minutos      | Bien                                 |
| Duplicación                     | SonarCloud              | 0,0 %                                                        | Bien                                 |
| Confiabilidad y seguridad        | SonarCloud              | A y A; 0 bugs, 0 vulnerabilidades, 0 security hotspots       | Bien                                 |

---

## Métricas propias en el código

### Cómo se calculan

El workflow `.github/workflows/backend-metrics.yml` corre en cada push, en cada pull request hacia `develop` o `main` y de forma manual. Instala `radon==6.0.1`, analiza las carpetas `app/` y `conf/` y guarda cuatro reportes en el artefacto `metricas-backend` (se conserva 30 días):

| Reporte                | Comando                                                                                            |
| ---------------------- | -------------------------------------------------------------------------------------------------- |
| `complejidad.txt`    | `radon cc app conf -s -a`                                                                        |
| `mantenibilidad.txt` | `radon mi app conf -s`                                                                           |
| `lineas.txt`         | `radon raw app conf -s`                                                                          |
| `acoplamiento.txt`   | Script de Python dentro del workflow que lee los `import` de cada archivo con el módulo `ast` |

### 1. Complejidad ciclomática

#### Qué mide

La cantidad de caminos independientes que tiene una función: cada `if`, `for`, `while`, `except` o condición con `and`/`or` suma uno. Entre más caminos, más casos hay que probar y más fácil es que se escape un error.

Radon asigna una letra según el valor: A (1 a 5), B (6 a 10), C (11 a 20), D (21 a 30), E (31 a 40) y F (más de 40).

#### Resultado

| Rango              | Funciones y clases |
| ------------------ | ------------------ |
| A (1 a 5)          | 201                |
| B (6 a 10)         | 18                 |
| C (11 a 20)        | 2                  |
| D, E o F           | 0                  |
| **Promedio** | **A (2,5)**  |

Las dos funciones en C están en `app/services/correo_recuperacion_service.py`:

- `validar_url_recuperacion`: 13
- `obtener_configuracion_correo`: 12

#### Cómo se interpreta

Un promedio de 2,5 quiere decir que la función típica del backend tiene dos o tres caminos y se puede probar con pocos casos. Las dos funciones en C validan muchas condiciones seguidas (protocolo, dominio, usuario y contraseña en la URL, puerto, variables de entorno del correo), y cada condición es un camino más.

#### Impacto

Estas dos funciones protegen la recuperación de contraseña, que es un flujo de seguridad. Con 12 o 13 caminos es más difícil revisar que se cubrieron todos los casos y más fácil romper uno al modificarlas. Por ahora tienen pruebas que las cubren (el archivo tiene 99 % de cobertura).

#### Acción de mejora

Dividir `validar_url_recuperacion` en funciones pequeñas, una por regla (`validar_protocolo`, `validar_host`, `validar_sin_credenciales`, `validar_puerto`), y que la función principal solo las llame en orden. En `obtener_configuracion_correo`, separar la lectura de las variables de SMTP de las de Microsoft Graph. Cada función nueva quedaría en A (1 a 5) y se podría probar por separado.

### 2. Índice de mantenibilidad

#### Qué mide

Un puntaje de 0 a 100 por archivo que combina el volumen del código (métrica de Halstead), la complejidad ciclomática y el número de líneas. Entre más alto, más fácil de entender y de modificar. Radon lo clasifica en A (20 a 100), B (10 a 19) y C (0 a 9).

#### Resultado

Los 52 archivos analizados están en A, con un promedio de 77,0. Los que tienen el puntaje más bajo son:

| Archivo                                         | Índice |
| ----------------------------------------------- | ------- |
| `app/vision/letras_estaticas.py`              | 37,1    |
| `app/services/correo_recuperacion_service.py` | 37,2    |
| `app/security.py`                             | 46,1    |
| `app/services/microsoft_oauth_service.py`     | 46,5    |
| `app/routes/usuarios.py`                      | 47,0    |

Hay un archivo que Radon no pudo analizar: `app/vision/letras_movimiento.py` empieza con una marca BOM (U+FEFF) y Radon falla al leerlo, tanto en complejidad como en mantenibilidad. Nuestro script de acoplamiento sí lo lee porque abre los archivos con `utf-8-sig`.

#### Cómo se interpreta

Todos los archivos están en A, así que ninguno es difícil de mantener según esta escala. Los que están cerca de 40 son los más largos o los que tienen más condiciones: `letras_estaticas.py` tiene las reglas de reconocimiento de cada letra y `correo_recuperacion_service.py` tiene las dos funciones en C del punto anterior.

#### Impacto

El índice indica que el backend se puede modificar sin mucho riesgo. El archivo sin medir es un punto ciego: no sabemos su complejidad real y es justo uno de los módulos con menos cobertura (22,6 %).

#### Acción de mejora

Guardar `letras_movimiento.py` como UTF-8 sin BOM para que Radon lo mida. Dividir `letras_estaticas.py` por grupos de letras o pasar las reglas a una tabla de datos, y aplicar la división de funciones del punto 1 en el servicio de correo.

### 3. Líneas de código y comentarios

#### Qué mide

El tamaño del código y cuánto de él está documentado.

#### Resultado

| Medida                                              | Valor |
| --------------------------------------------------- | ----- |
| Líneas totales (LOC)                               | 6.212 |
| Líneas de código (SLOC)                           | 4.571 |
| Líneas lógicas (LLOC)                             | 1.971 |
| Comentarios de una línea                           | 202   |
| Líneas de docstrings                               | 219   |
| Líneas en blanco                                   | 1.179 |
| Comentarios y docstrings sobre el total (C + M % L) | 7 %   |

#### Cómo se interpreta

El backend es pequeño (unas 4.500 líneas de código), así que se puede revisar completo. El 7 % de comentarios y docstrings es bajo: la mayoría de los archivos se entienden por los nombres de funciones y variables en español, pero los módulos con más reglas (visión y correo) tienen poca explicación de por qué se toma cada decisión.

#### Impacto

Con poca documentación en el código, entender las reglas de reconocimiento de cada letra depende de quien las escribió.

#### Acción de mejora

Agregar docstrings en los módulos con índice de mantenibilidad por debajo de 50, empezando por `letras_estaticas.py`, `movimientos.py` y `correo_recuperacion_service.py`, explicando qué valida cada regla y por qué.

### 4. Acoplamiento entre módulos

#### Qué mide

Cuánto depende cada módulo de los demás. Lo calcula un script propio que recorre los `import` de cada archivo de `app/` y `conf/` y cuenta dos valores:

- **Ce (acoplamiento eferente):** cuántos módulos internos importa ese módulo.
- **Ca (acoplamiento aferente):** cuántos módulos internos lo importan a él.

Un Ce alto quiere decir que el módulo se puede romper cuando cambia cualquiera de los que usa. Un Ca alto quiere decir que un cambio en ese módulo afecta a muchos otros.

#### Resultado

| Medida                             | Valor |
| ---------------------------------- | ----- |
| Módulos analizados                | 53    |
| Dependencias internas              | 89    |
| Ce promedio                        | 1,68  |
| Módulos sin dependencias internas | 5     |

| Mayor Ce (importa a muchos)   | Ce | Mayor Ca (lo importan muchos) | Ca |
| ----------------------------- | -- | ----------------------------- | -- |
| `app.main`                  | 14 | `conf.database`             | 13 |
| `app.routes.autenticacion`  | 7  | `app.security`              | 10 |
| `app.vision.reconocimiento` | 6  | `app.vision.movimientos`    | 5  |

#### Cómo se interpreta

En promedio cada módulo depende de menos de dos módulos internos, así que el backend tiene acoplamiento bajo y las capas (rutas, servicios, repositorios, visión) están separadas. El Ce de 14 en `app.main` es normal, porque es el archivo que arma la aplicación y registra todas las rutas. `conf.database` y `app.security` tienen el Ca más alto porque casi todos los servicios abren conexiones a la base de datos y casi todas las rutas validan el token.

La métrica también sirve para revisar `app.main`: sus 14 dependencias no incluyen los módulos de recuperación y restablecimiento de contraseña, que son justo las rutas que no están registradas en la aplicación.

#### Impacto

Un error o un cambio en `conf.database` o en `app.security` afecta a 13 y 10 módulos respectivamente. Esos dos archivos son los que más cuidado necesitan al modificarlos.

#### Acción de mejora

Mantener `conf.database` y `app.security` con una interfaz pequeña y estable, y cubrir sus funciones con pruebas antes de cualquier cambio. Registrar en `app.main` los routers de recuperación y restablecimiento de contraseña.

---

## Métricas de SonarQube

El análisis lo hace SonarCloud en el workflow `SonarQube.yml`, en cada push a `main` y en cada pull request. Analiza la carpeta `app` (configurada en `sonar-project.properties`) y recibe el reporte de cobertura que genera `pytest`.

| Métrica                      | Resultado                         |
| ----------------------------- | --------------------------------- |
| Quality Gate                  | Aprobado                          |
| Cobertura                     | 85,2 % (1.490 de 1.748 líneas)   |
| Duplicación                  | 0,0 % (0 bloques duplicados)      |
| Mantenibilidad                | A                                 |
| Code smells                   | 34, todos de severidad menor      |
| Deuda técnica                | 67 minutos (ratio de deuda 0,0 %) |
| Confiabilidad                 | A (0 bugs)                        |
| Seguridad                     | A (0 vulnerabilidades)            |
| Security hotspots             | 0                                 |
| Líneas de código analizadas | 4.495                             |

### Cobertura

#### Qué mide

El porcentaje de líneas del backend que ejecutan las pruebas automáticas.

#### Cómo se interpreta

Un 85,2 % quiere decir que 1.490 de las 1.748 líneas se ejecutan en alguna prueba. Está por encima del 80 % que exige `backend-ci.yml`. Los servicios (95,3 %) y las rutas (93,9 %) están casi completos; la carpeta `app/vision` baja al 61,6 %, sobre todo por el prototipo `app/vision/prototype/main.py`, que tiene 0 % y no lo usa la API. El detalle está en el [plan de pruebas](../pruebas/plan_pruebas.md).

#### Acción de mejora

Excluir el prototipo del análisis (sin él la cobertura sería del 90,6 %) y probar la lógica de movimiento de la visión con datos guardados de los puntos de la mano.

### Mantenibilidad (A)

#### Qué mide

SonarCloud estima cuánto tiempo tomaría corregir todos los code smells (deuda técnica) y lo compara con el tiempo de escribir el código. La calificación es A cuando la deuda es como máximo el 5 % de ese tiempo.

#### Cómo se interpreta

La deuda es de 67 minutos, que frente al costo estimado del código da un ratio de 0,0 %. Una A aquí quiere decir que el código casi no tiene deuda técnica pendiente. De los 34 code smells, 32 son de la misma regla: `with` anidados que se pueden combinar en uno solo (`with obtener_conexion() as conexion, conexion.cursor() as cursor:`). Los otros dos son una excepción redundante en un `except` de `app/services/vision_service.py` y una variable llamada `muñeca` en `app/vision/movimientos.py`, que no cumple la convención de nombres por la ñ.

#### Acción de mejora

Combinar los `with` anidados en los servicios (la mayoría están en `progreso_service.py`, `usuarios_service.py`, `autenticacion_service.py` y `sesiones_service.py`), quitar la excepción redundante y renombrar la variable a `muneca`. Son cambios pequeños y dejarían el proyecto en 0 code smells.

### Duplicación (0,0 %)

#### Qué mide

El porcentaje de líneas que están copiadas en más de un lugar.

#### Cómo se interpreta

No hay bloques duplicados. Cuando un cambio se hace en un solo lugar, no queda una copia vieja del mismo código en otro archivo.

### Confiabilidad y seguridad (A y A)

#### Qué miden

La confiabilidad cuenta los bugs que SonarCloud detecta en el código (por ejemplo, variables que pueden ser `None` o recursos que no se cierran). La seguridad cuenta las vulnerabilidades y los puntos sensibles (security hotspots) que hay que revisar.

#### Cómo se interpreta

Con 0 bugs, 0 vulnerabilidades y 0 hotspots las dos calificaciones son A. SonarCloud no encontró errores conocidos ni código inseguro en el backend. Esto no reemplaza las pruebas: el router de recuperación de contraseña sin registrar no es un error que SonarCloud pueda detectar.

---

## Impacto en la calidad del sistema

Las métricas muestran un backend fácil de mantener: la complejidad promedio es baja, todos los archivos medidos están en A, no hay código duplicado y SonarCloud no encuentra bugs ni vulnerabilidades. Con las pruebas cubriendo el 85,2 % del código, un cambio que rompa algo existente se detecta en el CI antes de llegar a `develop`.

Los puntos débiles, donde un cambio tiene más riesgo, están en pocos archivos: el servicio de correo de recuperación (las dos funciones más complejas), los módulos de visión (menos cobertura, un archivo sin medir y pocos comentarios) y los dos módulos de los que depende casi todo (`conf.database` y `app.security`).

---

## Acciones de mejora

| Prioridad | Problema                                                            | Acción                                                                                                    | Cómo lo corrige                                                                    |
| --------- | ------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| 1         | Las rutas de recuperación de contraseña no están en `app.main` | Registrar los routers de recuperación y restablecimiento en `app/main.py`                               | La funcionalidad queda disponible y `app.main` pasa a depender de esos módulos   |
| 2         | `letras_movimiento.py` no se puede medir                          | Guardarlo como UTF-8 sin BOM                                                                               | Radon puede calcular su complejidad y mantenibilidad                                |
| 3         | Dos funciones con complejidad C                                     | Dividir `validar_url_recuperacion` y `obtener_configuracion_correo` en funciones de una regla cada una | Cada función queda en A y se prueba por separado                                   |
| 4         | 34 code smells menores                                              | Combinar los `with` anidados, quitar la excepción redundante y renombrar `muñeca`                    | SonarCloud queda en 0 code smells                                                   |
| 5         | El prototipo baja la cobertura                                      | Excluir `app/vision/prototype/` del análisis o sacarlo de `app/`                                      | La cobertura mide solo el código que usa la API (90,6 %)                           |
| 6         | Pocos comentarios en visión y correo                               | Agregar docstrings en los módulos con índice de mantenibilidad menor a 50                                | Las reglas de reconocimiento y validación quedan explicadas en el código          |
| 7         | `conf.database` y `app.security` afectan a muchos módulos      | Mantener su interfaz pequeña y probar sus funciones antes de cambiarlas                                   | Un cambio en esos módulos no rompe en silencio a los 13 y 10 que dependen de ellos |
