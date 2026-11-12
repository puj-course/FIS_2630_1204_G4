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
