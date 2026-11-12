# Diagrama de clases — Patrón Strategy en el reconocimiento de señas

![Diagrama de clases del patrón Strategy](./DiagramadeClasesPatronStrategy.png)

## Descripción

Este diagrama muestra cómo se aplicó el patrón **Strategy** en el módulo de visión de SignIA para separar las diferentes formas de realizar el reconocimiento de señas.

Durante el reconocimiento existen señas que pueden identificarse utilizando únicamente la posición actual de la mano y otras que necesitan analizar una secuencia de movimiento. Para evitar concentrar ambos comportamientos dentro de una misma clase, se definió `EstrategiaReconocimiento` como contrato común y se crearon las estrategias `ReconocimientoEstatico` y `ReconocimientoMovimiento`.

`ReconocedorMano` funciona como el contexto del patrón. Esta clase mantiene una referencia a una estrategia y delega en ella la operación de reconocimiento. Además, permite cambiar la estrategia utilizada sin modificar el funcionamiento general del contexto.

Archivos de código relacionados:

- `app/vision/estrategia_reconocimiento.py`, contiene la estructura principal del patrón Strategy.
- `app/vision/reconocimiento.py`, contiene elementos utilizados durante el reconocimiento de la mano.
- `app/vision/letras_estaticas.py`, contiene lógica relacionada con el reconocimiento de señas estáticas.
- `app/vision/letras_movimiento.py`, contiene lógica relacionada con las señas que necesitan movimiento.
- `src/tests/test_estrategias_reconocimiento.py`, contiene las pruebas de las estrategias y del cambio de comportamiento.

## Roles del patrón

| **Rol (GoF)** | **Elemento en SignIA** | **Responsabilidad** |
| --- | --- | --- |
| **Client** | `reconocimiento` | Utiliza el contexto para iniciar el reconocimiento de una seña. |
| **Context** | `ReconocedorMano` | Mantiene la estrategia actual y delega en ella la operación de reconocimiento. |
| **Strategy** | `EstrategiaReconocimiento` | Define la operación común que deben implementar las diferentes estrategias. |
| **Concrete Strategy** | `ReconocimientoEstatico` | Implementa el reconocimiento utilizado para señas estáticas. |
| **Concrete Strategy** | `ReconocimientoMovimiento` | Implementa el reconocimiento utilizado para señas que necesitan analizar movimiento. |

## Notación

- **`«utility»`** se utiliza para representar el módulo `reconocimiento`, ya que corresponde a un módulo de Python y no a una clase.
- **`«context»`** identifica a `ReconocedorMano` como el elemento que utiliza una estrategia durante el reconocimiento.
- **`«abstract»`** representa a `EstrategiaReconocimiento`, debido a que define el comportamiento común que deben implementar las estrategias concretas.
- `ReconocimientoEstatico` y `ReconocimientoMovimiento` son las estrategias concretas del patrón.

## Elementos

### `EstrategiaReconocimiento`

Representa la estrategia general del patrón. Su responsabilidad es definir la operación que deben cumplir las diferentes formas de reconocimiento.

| **Operación** | **Qué hace** |
| --- | --- |
| `reconocer(...)` | Define la operación común utilizada para realizar el reconocimiento. |

La estrategia no determina directamente si el reconocimiento es estático o requiere movimiento. Esa responsabilidad queda en las clases concretas que implementan este contrato.

### `ReconocedorMano`

Representa el contexto del patrón Strategy. Mantiene una referencia a una implementación de `EstrategiaReconocimiento` y utiliza esa referencia cada vez que debe realizarse un reconocimiento.

| **Elemento** | **Qué hace** |
| --- | --- |
| `estrategia : EstrategiaReconocimiento` | Mantiene la estrategia que se está utilizando actualmente. |
| `reconocer(...)` | Delega la operación de reconocimiento en la estrategia actual. |
| `cambiar_estrategia(estrategia : EstrategiaReconocimiento) : None` | Permite reemplazar la estrategia utilizada por el contexto. |

El contexto no necesita conocer los detalles internos del algoritmo utilizado. Solamente conoce el contrato `EstrategiaReconocimiento` y delega la operación correspondiente.

### `ReconocimientoEstatico`

Es una estrategia concreta encargada del reconocimiento de señas que pueden identificarse a partir de la configuración actual de la mano.

| **Operación** | **Qué hace** |
| --- | --- |
| `reconocer(...)` | Ejecuta el comportamiento correspondiente al reconocimiento estático. |

Esta clase implementa el contrato definido por `EstrategiaReconocimiento`.

### `ReconocimientoMovimiento`

Es una estrategia concreta utilizada cuando la seña necesita analizar información relacionada con el movimiento.

| **Operación** | **Qué hace** |
| --- | --- |
| `reconocer(...)` | Ejecuta el comportamiento correspondiente al reconocimiento con movimiento. |

Al igual que `ReconocimientoEstatico`, implementa el mismo contrato, por lo que ambas estrategias pueden ser utilizadas por `ReconocedorMano`.

### Cliente

El módulo `reconocimiento` actúa como cliente del patrón y utiliza `ReconocedorMano` para ejecutar el reconocimiento.

El cliente no necesita ejecutar directamente los algoritmos correspondientes a cada tipo de seña. El contexto recibe o mantiene la estrategia necesaria y posteriormente delega en ella el reconocimiento.

## Relaciones

| **Relación** | **Tipo** | **Significado** |
| --- | --- | --- |
| `reconocimiento` → `ReconocedorMano` | Dependencia `«use»` | El cliente utiliza el contexto para realizar el reconocimiento. |
| `ReconocedorMano` → `EstrategiaReconocimiento` | Asociación dirigida, rol `estrategia`, multiplicidad `1` | El contexto mantiene una referencia a la estrategia que utiliza. |
| `ReconocimientoEstatico` → `EstrategiaReconocimiento` | Generalización | La estrategia concreta implementa el comportamiento para reconocimiento estático. |
| `ReconocimientoMovimiento` → `EstrategiaReconocimiento` | Generalización | La estrategia concreta implementa el comportamiento para reconocimiento con movimiento. |

La relación entre `ReconocedorMano` y `EstrategiaReconocimiento` permite que el contexto trabaje con cualquiera de las estrategias concretas sin depender directamente de una implementación específica.

## Funcionamiento del patrón

Cuando debe realizarse un reconocimiento, `ReconocedorMano` utiliza la estrategia que tiene asignada y llama a su operación `reconocer(...)`. La estrategia concreta es la encargada de ejecutar el comportamiento correspondiente.

Si el reconocimiento requiere un comportamiento diferente, el contexto puede cambiar su estrategia mediante `cambiar_estrategia(...)`. De esta manera, el objeto `ReconocedorMano` puede seguir siendo el mismo mientras cambia el algoritmo utilizado.

Por ejemplo, el contexto puede trabajar inicialmente con `ReconocimientoEstatico` y posteriormente utilizar `ReconocimientoMovimiento`. Como las dos implementan `EstrategiaReconocimiento`, el cambio puede realizarse sin modificar el código que utiliza el contexto.

## Cambio de estrategia

Una de las partes principales de la implementación es la posibilidad de cambiar el comportamiento durante la ejecución.

El flujo puede representarse de la siguiente manera:

```text
ReconocedorMano
      |
      | estrategia
      v
ReconocimientoEstatico
```

Posteriormente:

```text
ReconocedorMano
      |
      | cambiar_estrategia(...)
      v
ReconocimientoMovimiento
```

El contexto mantiene la misma responsabilidad y únicamente cambia el objeto al que delega el reconocimiento.

## Pruebas

Las pruebas de `test_estrategias_reconocimiento.py` permiten comprobar el comportamiento de las diferentes estrategias y su utilización desde el contexto.

Entre los aspectos evaluados se encuentran:

- el funcionamiento de las estrategias concretas;
- la delegación del reconocimiento desde `ReconocedorMano`;
- el uso de una estrategia estática;
- el uso de una estrategia de movimiento;
- el cambio de estrategia dentro del mismo contexto;
- la conservación del contrato común definido por `EstrategiaReconocimiento`.

Estas pruebas permiten comprobar que el contexto no queda acoplado a una única forma de reconocimiento y que las estrategias pueden intercambiarse manteniendo la misma interfaz.

## Elementos omitidos

| **Omitido** | **Motivo** |
| --- | --- |
| `GestorDetectoresCompartido` | Corresponde a la implementación del patrón Singleton y no forma parte directa de Strategy. |
| `DetectorMano` | Participa en la detección de la mano, pero no define la estructura del patrón Strategy. |
| `DecoradorMedicionTiempo` | Pertenece al patrón Decorator y agrega comportamiento alrededor del reconocimiento. |
| MediaPipe | Es utilizado internamente durante el reconocimiento, pero no participa directamente en la estructura del patrón. |
| OpenCV | Se utiliza para el procesamiento de imágenes y no forma parte de Strategy. |
| Reglas individuales de las letras | Son utilizadas por las estrategias, pero incluirlas haría el diagrama más grande sin aportar a la explicación del patrón. |
| Servicios de sesiones, resultados y progreso | Se ejecutan en otras partes del flujo de SignIA y no intervienen en la selección de la estrategia. |

El diagrama se concentra en los elementos necesarios para mostrar cómo `ReconocedorMano` puede trabajar con diferentes algoritmos de reconocimiento mediante un contrato común y cambiar entre ellos sin modificar el contexto.