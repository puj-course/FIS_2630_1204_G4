# Diagrama de clases — Patrón Singleton en la gestión de detectores

![Diagrama de clases del patrón Singleton](./DiagramadeClasesPatronSingleton.png)

## Descripción

Este diagrama muestra cómo se aplicó el patrón **Singleton** en el módulo de visión de SignIA para administrar los detectores de manos utilizados durante el reconocimiento de señas.

El servicio de visión necesita utilizar detectores de MediaPipe cada vez que procesa una imagen. Crear nuevamente estos recursos para cada solicitud generaría instancias innecesarias y dificultaría su administración. Por esta razón, se utiliza `GestorDetectoresCompartido`, que mantiene una única instancia del gestor durante la ejecución de la aplicación y se encarga de crear, reutilizar y cerrar los objetos `DetectorMano`.

