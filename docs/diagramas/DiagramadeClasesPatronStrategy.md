# Diagrama de clases — Patrón Strategy en el reconocimiento de señas

![Diagrama de clases del patrón Strategy](./DiagramadeClasesPatronStrategy.png)

## Descripción

Este diagrama muestra cómo se aplicó el patrón **Strategy** en el módulo de visión de SignIA para separar las diferentes formas de realizar el reconocimiento de señas.

Durante el reconocimiento existen señas que pueden identificarse utilizando únicamente la posición actual de la mano y otras que necesitan analizar una secuencia de movimiento. Para evitar concentrar ambos comportamientos dentro de una misma clase, se definió `EstrategiaReconocimiento` como contrato común y se crearon las estrategias `ReconocimientoEstatico` y `ReconocimientoMovimiento`.

`ReconocedorMano` funciona como el contexto del patrón. Esta clase mantiene una referencia a una estrategia y delega en ella la operación de reconocimiento. Además, permite cambiar la estrategia utilizada sin modificar el funcionamiento general del contexto.
