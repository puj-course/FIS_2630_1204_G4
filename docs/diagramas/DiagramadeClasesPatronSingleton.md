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
