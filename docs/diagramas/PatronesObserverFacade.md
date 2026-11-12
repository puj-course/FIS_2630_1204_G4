# Patrones de diseño en SignIA: Observer y Facade

Estos diagramas se centran en el frontend de SignIA. Para cada patrón se presenta una vista de nivel 3 (componentes) y una de nivel 4 (código) del modelo C4. Las vistas de nivel 4 se representan mediante diagramas de clases Mermaid y muestran únicamente clases e interfaces existentes en el código.

## Observer — eventos de práctica

### Nivel 3: componentes

```mermaid
flowchart LR
    subgraph Frontend["Frontend de SignIA"]
        Reconocimiento["Reconocimiento de señas<br/>ResultadoReconocimiento"]
        Eventos["Gestión de eventos de práctica<br/>EventosPractica"]
        Practica["Observadores definidos en<br/>Practica"]
        Historial["Vista del historial<br/>HistorialReconocimiento"]
        Confirmacion["Vista de confirmación<br/>ConfirmacionAprendizaje"]
    end

    Reconocimiento -->|"Llama a notificar(evento)"| Eventos
    Eventos -->|"Llama a actualizar(evento)<br/>en cada observador"| Practica
    Practica -->|"Actualiza los datos mostrados"| Historial
    Practica -->|"Muestra la confirmación"| Confirmacion
```

`ResultadoReconocimiento` origina los eventos. `EventosPractica` notifica a todos los observadores que mantiene. Cada observador recibe el evento mediante `actualizar(evento)` y decide si debe reaccionar. Las vistas de historial y confirmación no son observadores directos: muestran el estado gestionado desde `Practica`.

### Nivel 4: diagrama de clases

Este diagrama muestra únicamente las operaciones que intervienen en la notificación.

```mermaid
classDiagram
    direction LR

    class SujetoPractica {
        <<interface>>
        +notificar(evento: EventoPractica) void
    }

    class ObservadorPractica {
        <<interface>>
        +actualizar(evento: EventoPractica) void
    }

    class EventosPractica {
        -observadores: Set~ObservadorPractica~
        +notificar(evento: EventoPractica) void
    }

    EventosPractica ..|> SujetoPractica : implementa
    EventosPractica "1" o-- "0..*" ObservadorPractica : notifica a todos
```

El recorrido es: `ResultadoReconocimiento` llama a `notificar(evento)` → `EventosPractica` recorre sus observadores → llama a `actualizar(evento)` en cada uno. El tipo `EventoPractica` es una unión de TypeScript, no una clase.

Los observadores concretos, `observadorHistorial` y `observadorConfirmacion`, son objetos creados dentro de la función React `Practica`; no se representan como clases que no existen. El código también contiene operaciones para agregar y retirar observadores, pero se omiten aquí para enfocar el diagrama en **notificar → actualizar**.

## Facade — registro de práctica

### Nivel 3: componentes

```mermaid
flowchart LR
    subgraph Frontend["Frontend de SignIA"]
        Cliente["Interfaz de reconocimiento<br/>ResultadoReconocimiento"]
        Fachada["Registro de práctica<br/>FachadaRegistroPractica"]
        Auth["Servicio de autenticación"]
        Letras["Servicio de letras"]
        Sesiones["Servicio de sesiones"]
        Resultados["Servicio de resultados"]
        Progreso["Servicio de progreso"]
    end

    Cliente -->|"Solicita registrar intento<br/>o progreso"| Fachada
    Fachada -->|"Obtiene sesión del usuario"| Auth
    Fachada -->|"Resuelve la letra"| Letras
    Fachada -->|"Gestiona sesión de reconocimiento"| Sesiones
    Fachada -->|"Guarda el intento"| Resultados
    Fachada -->|"Registra aprendizaje"| Progreso
```

`FachadaRegistroPractica` coordina funciones de los servicios existentes. `ResultadoReconocimiento` utiliza sus operaciones públicas en lugar de coordinar directamente esos pasos para el registro de práctica.

### Nivel 4: diagrama de clases

```mermaid
classDiagram
    direction LR

    class RegistroIntentoPracticaEntrada {
        <<interface>>
        +token: string
        +idLetraObjetivo: number
        +letraDetectada: string
        +confianza: number
        +sigueActivo: function
    }

    class SubsistemasRegistroPractica {
        <<interface>>
        +obtenerSesion
        +obtenerIdLetra
        +obtenerSesionReconocimiento
        +crearSesionReconocimiento
        +guardarSesionReconocimiento
        +limpiarSesionReconocimiento
        +registrarResultadoReconocimiento
        +registrarProgreso
    }

    class FachadaRegistroPractica {
        -subsistemas: SubsistemasRegistroPractica
        +registrarIntento(datos: RegistroIntentoPracticaEntrada) Promise
        +registrarProgreso(idLetra: number, token: string) Promise
        -limpiarSesionInvalida(idSesion: number) void
    }

    FachadaRegistroPractica --> SubsistemasRegistroPractica : depende de
    FachadaRegistroPractica ..> RegistroIntentoPracticaEntrada : recibe
```

`FachadaRegistroPractica` es la clase del patrón. Sus métodos públicos `registrarIntento` y `registrarProgreso` forman la interfaz simplificada que utiliza el cliente.

`SubsistemasRegistroPractica` **no es una interfaz implementada por la fachada**: describe las funciones de servicio que la fachada necesita como dependencias. `RegistroIntentoPracticaEntrada` define los datos de entrada de `registrarIntento`. Las funciones de los servicios y el objeto `subsistemasPorDefecto` no se dibujan como clases porque no lo son.

La fachada simplifica la coordinación, pero no convierte el guardado del intento y del progreso en una transacción única. El intento puede quedar registrado aunque falle una operación posterior de progreso.

## Diferencia entre los patrones

Observer desacopla la comunicación de eventos: quien origina un evento no necesita conocer las reacciones de cada observador. Facade simplifica la coordinación de servicios: el cliente utiliza operaciones de la fachada en lugar de ejecutar directamente cada paso del registro de práctica.
