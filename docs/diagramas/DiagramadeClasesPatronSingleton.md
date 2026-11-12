# Diagrama de clases — Patrón Singleton en la gestión de detectores

![Diagrama de clases del patrón Singleton](./DiagramadeClasesPatronSingleton.png)

## Descripción

Este diagrama muestra cómo se aplicó el patrón **Singleton** en el módulo de visión de SignIA para administrar los detectores de manos utilizados durante el reconocimiento de señas.

El servicio de visión necesita utilizar detectores de MediaPipe cada vez que procesa una imagen. Crear nuevamente estos recursos para cada solicitud generaría instancias innecesarias y dificultaría su administración. Por esta razón, se utiliza `GestorDetectoresCompartido`, que mantiene una única instancia del gestor durante la ejecución de la aplicación y se encarga de crear, reutilizar y cerrar los objetos `DetectorMano`.

Archivos de código relacionados:

- `app/vision/gestor_detectores.py`, contiene el contrato y la implementación Singleton.
- `app/vision/detector.py`, contiene `DetectorMano`, recurso administrado por el gestor.
- `app/services/vision_service.py`, cliente que utiliza el gestor durante el procesamiento.
- `src/tests/test_gestor_detectores.py`, contiene las pruebas relacionadas con el Singleton y la reutilización de detectores.

## Roles del patrón

| **Rol** | **Elemento en SignIA** | **Responsabilidad** |
| --- | --- | --- |
| **Client** | `vision_service` | Utiliza el gestor para acceder a los detectores durante el procesamiento de imágenes. |
| **Singleton** | `GestorDetectoresCompartido` | Controla que exista una única instancia del gestor y administra los detectores disponibles. |
| **Contrato** | `GestorDetectores` | Define las operaciones que debe ofrecer un gestor de detectores. |
| **Recurso administrado** | `DetectorMano` | Realiza la detección de la mano utilizando MediaPipe. |

## Notación

- **`«utility»`** se utiliza para representar `vision_service`, ya que corresponde a un módulo de Python que expone funciones y no a una clase.
- **`«abstract»`** se utiliza para representar `GestorDetectores`, debido a que define el comportamiento que debe cumplir el gestor.
- **`«singleton»`** identifica a `GestorDetectoresCompartido` como la clase encargada de mantener una única instancia del gestor.
- `DetectorMano` es una clase normal y representa el recurso administrado por el Singleton.

## Elementos

### `GestorDetectores`

Es el contrato utilizado para definir las operaciones principales relacionadas con los detectores.

| **Operación** | **Qué hace** |
| --- | --- |
| `detectar(imagen, tiempo_actual=None)` | Define la operación utilizada para realizar la detección sobre una imagen. |
| `cerrar() : None` | Define la operación utilizada para liberar los detectores administrados. |

### `GestorDetectoresCompartido`

Es la implementación del patrón Singleton. Controla la creación de su propia instancia y administra los detectores utilizados por el módulo de visión.

| **Elemento** | **Qué hace** |
| --- | --- |
| `_instancia : GestorDetectoresCompartido` | Mantiene la referencia a la única instancia del gestor. |
| `_bloqueo_instancia : Lock` | Protege la creación de la instancia cuando existen varias ejecuciones al mismo tiempo. |
| `_detectores : dict` | Almacena los detectores creados para poder reutilizarlos. |
| `_bloqueo_operaciones : Lock` | Protege las operaciones realizadas sobre los detectores compartidos. |
| `__new__() : GestorDetectoresCompartido` | Controla la creación de la instancia y devuelve la existente cuando ya fue creada. |
| `detectar(imagen, tiempo_actual=None)` | Obtiene el detector correspondiente y realiza la detección. |
| `cerrar() : None` | Cierra los detectores existentes y libera los recursos administrados. |

La implementación utiliza `__new__()` en lugar de un método `getInstance()`. Cuando se solicita un nuevo `GestorDetectoresCompartido`, primero se verifica si la instancia ya existe. Si existe, se devuelve la misma referencia; si todavía no existe, se crea y se almacena.

### `DetectorMano`

Representa el recurso administrado por el Singleton. El gestor puede crear y conservar detectores según el modo requerido durante el procesamiento.

| **Operación o atributo** | **Qué hace** |
| --- | --- |
| `modo_video : bool` | Indica el modo utilizado por el detector. |
| `detector` | Mantiene la referencia al detector utilizado internamente. |
| `DetectorMano(modo_video=True)` | Crea el detector según el modo requerido. |
| `detectar(imagen, tiempo_actual=None)` | Realiza la detección de la mano sobre la imagen recibida. |
| `cerrar() : None` | Libera los recursos utilizados por el detector. |

### Cliente

`vision_service` utiliza una instancia de `GestorDetectoresCompartido` para realizar las detecciones necesarias durante el reconocimiento.

El módulo mantiene una referencia al gestor y la utiliza desde el procesamiento de imágenes. También utiliza el gestor cuando es necesario cerrar los detectores al finalizar el servicio.

## Relaciones

| **Relación** | **Tipo** | **Significado** |
| --- | --- | --- |
| `vision_service` → `GestorDetectoresCompartido` | Dependencia `«use»` | El servicio de visión utiliza la instancia compartida del gestor. |
| `GestorDetectoresCompartido` → `GestorDetectores` | Generalización | El Singleton implementa el contrato definido por `GestorDetectores`. |
| `GestorDetectoresCompartido` → `DetectorMano` | Composición, rol `detectores` | El gestor crea, conserva, reutiliza y cierra los detectores. |

La multiplicidad desde `GestorDetectoresCompartido` hacia `DetectorMano` puede representarse como **1 a 0..2**, debido a que existe una única instancia del gestor y esta puede mantener los detectores necesarios para los diferentes modos de procesamiento.

El patrón garantiza que exista un único `GestorDetectoresCompartido`. Esto no significa que exista un único `DetectorMano`, ya que el gestor puede administrar más de un detector según el modo requerido.

## Funcionamiento del Singleton

Cuando `vision_service` necesita realizar una detección, utiliza `GestorDetectoresCompartido()`. La creación pasa por `__new__()`, que comprueba si ya existe una instancia del gestor. Si todavía no existe, la crea; en las siguientes solicitudes devuelve la misma instancia.

El gestor revisa después si ya existe un `DetectorMano` adecuado para la operación. Cuando existe, lo reutiliza, y cuando todavía no ha sido creado, genera uno nuevo y lo conserva dentro de `_detectores`. De esta manera, la creación y el cierre de estos recursos quedan concentrados en un mismo punto.

## Pruebas

Las pruebas de `test_gestor_detectores.py` comprueban el comportamiento del Singleton y la administración de los detectores.

Entre los casos evaluados se verifica:

- que varias llamadas a `GestorDetectoresCompartido()` devuelvan la misma instancia;
- que la instancia continúe siendo única cuando se solicita desde diferentes hilos;
- que los detectores existentes sean reutilizados;
- que los detectores correspondientes a distintos modos se mantengan separados;
- que `cerrar()` libere los detectores administrados;
- que los detectores puedan volver a crearse después de ser cerrados.

Estas pruebas permiten comprobar tanto la existencia de una única instancia del gestor como el manejo de los recursos que administra.

## Elementos omitidos

| **Omitido** | **Motivo** |
| --- | --- |
| MediaPipe `HandLandmarker` | Es utilizado internamente por `DetectorMano`, pero no participa directamente en la estructura del patrón Singleton. |
| Estrategias de reconocimiento | Utilizan los resultados de la detección, pero pertenecen al proceso de reconocimiento y no al Singleton. |
| Historial de movimiento | Forma parte del procesamiento de señas con movimiento y no de la administración de detectores. |
| Reglas de reconocimiento de letras | Se ejecutan después de detectar la mano y no intervienen en la creación de la instancia compartida. |
| OpenCV | Se utiliza durante el procesamiento de imágenes, pero no participa directamente en el patrón. |

El diagrama se concentra únicamente en las clases y módulos necesarios para mostrar cómo se crea una única instancia de `GestorDetectoresCompartido` y cómo esta administra los objetos `DetectorMano`.