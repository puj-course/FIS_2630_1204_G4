# Patrones de diseño en SignIA: Observer y Facade

Estos diagramas se centran en el frontend de SignIA. Para cada patrón se presenta una vista de nivel 3 (componentes) y una de nivel 4 (código) del modelo C4. Las vistas de nivel 4 se representan mediante diagramas de clases Mermaid y muestran únicamente clases e interfaces existentes en el código.

## Observer — eventos de práctica

### Nivel 3: componentes

```mermaid
flowchart LR
    subgraph Frontend["Frontend de SignIA"]
        Reconocimiento["Reconocimiento de señas<br/>ResultadoReconocimiento"]
        Eventos["Gestión de eventos de práctica<br/>EventosPractica"]
        Practica["Coordinación de práctica<br/>Practica"]
        Historial["Vista del historial<br/>HistorialReconocimiento"]
        Confirmacion["Vista de confirmación<br/>ConfirmacionAprendizaje"]
    end

    Reconocimiento -->|"Publica intento registrado<br/>o progreso registrado"| Eventos
    Practica -->|"Suscribe y desuscribe<br/>sus observadores"| Eventos
    Eventos -->|"Notifica los eventos"| Practica
    Practica -->|"Actualiza los datos mostrados"| Historial
    Practica -->|"Muestra la confirmación"| Confirmacion
```

`ResultadoReconocimiento` publica un evento después de guardar un intento y otro después de registrar correctamente el progreso. `Practica` coordina las reacciones: actualiza el historial o muestra la confirmación. Las vistas no son observadores directos.

### Nivel 4: diagrama de clases

```mermaid
classDiagram
    direction LR

    class SujetoPractica {
        <<interface>>
        +suscribir(observador: ObservadorPractica) void
        +desuscribir(observador: ObservadorPractica) void
        +notificar(evento: EventoPractica) void
    }

    class ObservadorPractica {
        <<interface>>
        +actualizar(evento: EventoPractica) void
    }

    class EventosPractica {
        -observadores: Set~ObservadorPractica~
        +suscribir(observador: ObservadorPractica) void
        +desuscribir(observador: ObservadorPractica) void
        +notificar(evento: EventoPractica) void
    }

    EventosPractica ..|> SujetoPractica : implementa
    EventosPractica "1" o-- "0..*" ObservadorPractica : mantiene suscripciones
    SujetoPractica ..> ObservadorPractica : registra
```

`EventosPractica` es la clase concreta que implementa `SujetoPractica`. Almacena referencias a elementos que cumplen `ObservadorPractica` y llama a `actualizar` al notificarlos. `EventoPractica` es un **tipo unión de TypeScript**, no una clase, por eso aparece en las firmas pero no como clase del diagrama.

Los observadores concretos del proyecto, `observadorHistorial` y `observadorConfirmacion`, son **objetos literales creados dentro de la función React `Practica`**. Tampoco se dibujan como clases porque no lo son. `ResultadoReconocimiento` es otra función React: origina la notificación, pero no implementa ninguna de estas interfaces.

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
