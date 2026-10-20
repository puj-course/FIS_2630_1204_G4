# Patrones de diseño en SignIA: Observer y Facade

Estos diagramas se centran en el frontend de SignIA. Para cada patrón se presenta una vista de nivel 3 (componentes) y una de nivel 4 (código) del modelo C4.

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

`ResultadoReconocimiento` publica un evento después de guardar un intento y otro después de registrar correctamente el progreso. `Practica` coordina las reacciones: actualiza el historial o muestra la confirmación de aprendizaje. Las vistas de historial y confirmación no son observadores por sí mismas; muestran el estado que gestiona `Practica`.

### Nivel 4: código

```mermaid
flowchart TB
    Tipo["Tipo EventoPractica<br/>intentoRegistrado | progresoRegistrado"]
    ISujeto["Interfaz SujetoPractica<br/>suscribir · desuscribir · notificar"]
    IObservador["Interfaz ObservadorPractica<br/>actualizar(evento)"]
    Clase["Clase EventosPractica<br/>Set de observadores"]
    Instancia["Objeto eventosPractica<br/>instancia de EventosPractica"]
    Practica["Función React Practica"]
    Resultado["Función React ResultadoReconocimiento"]
    ObsHistorial["Objeto observadorHistorial"]
    ObsConfirmacion["Objeto observadorConfirmacion"]

    Clase -.->|"implementa"| ISujeto
    Clase -->|"almacena y notifica"| IObservador
    ISujeto -->|"usa"| Tipo
    IObservador -->|"recibe"| Tipo

    Practica -->|"crea"| Instancia
    Instancia -->|"es instancia de"| Clase
    Practica -->|"crea y suscribe"| ObsHistorial
    Practica -->|"crea y suscribe"| ObsConfirmacion
    ObsHistorial -.->|"cumple"| IObservador
    ObsConfirmacion -.->|"cumple"| IObservador

    Resultado -->|"recibe el sujeto y llama notificar"| Instancia
    Instancia -->|"llama actualizar"| ObsHistorial
    Instancia -->|"llama actualizar"| ObsConfirmacion
```

- **Sujeto observado:** la instancia `eventosPractica` de la clase `EventosPractica`.
- **Observadores:** los objetos `observadorHistorial` y `observadorConfirmacion`, creados dentro de `Practica`.
- **Contrato:** `SujetoPractica` define la suscripción y notificación; `ObservadorPractica` define `actualizar`.
- **Emisor:** `ResultadoReconocimiento` llama a `notificar`, pero no es el sujeto ni un observador.

Los observadores se desuscriben durante la limpieza del efecto de React. Así se evita que una instancia de práctica ya desmontada siga reaccionando a eventos.

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

La fachada ofrece al componente de reconocimiento una entrada más simple para registrar la práctica. La coordinación de autenticación, letras, sesiones, resultados y progreso queda concentrada en `FachadaRegistroPractica`, mientras los servicios existentes conservan sus responsabilidades.

### Nivel 4: código

```mermaid
flowchart TB
    Cliente["Función React<br/>ResultadoReconocimiento"]
    Instancia["Objeto fachada<br/>instancia de FachadaRegistroPractica"]
    Clase["Clase FachadaRegistroPractica<br/>registrarIntento · registrarProgreso"]
    Contrato["Interfaz SubsistemasRegistroPractica<br/>dependencias requeridas"]
    Defecto["Objeto subsistemasPorDefecto"]

    Auth["Funciones de autenticación"]
    Letras["Funciones de letras"]
    Sesiones["Funciones de sesiones"]
    Resultados["Funciones de resultados"]
    Progreso["Funciones de progreso"]

    Cliente -->|"crea y utiliza"| Instancia
    Instancia -->|"es instancia de"| Clase
    Clase -->|"depende de"| Contrato
    Clase -->|"usa por defecto o recibe inyectado"| Defecto
    Defecto -.->|"cumple estructuralmente"| Contrato

    Defecto --> Auth
    Defecto --> Letras
    Defecto --> Sesiones
    Defecto --> Resultados
    Defecto --> Progreso
```

- **Cliente:** `ResultadoReconocimiento`, que utiliza la fachada.
- **Fachada:** la clase `FachadaRegistroPractica` y su instancia.
- **Subsistemas:** las funciones de los servicios existentes. No se crearon clases nuevas para ellos.
- **Contrato de dependencias:** `SubsistemasRegistroPractica` describe las funciones que necesita la fachada. La clase depende de esa interfaz, pero no la implementa; `subsistemasPorDefecto` es el objeto que cumple su estructura.

La fachada simplifica la coordinación, pero no convierte el guardado del intento y del progreso en una transacción única. El intento puede quedar registrado aunque falle una operación posterior de progreso.

## Diferencia entre los patrones

Observer desacopla la comunicación de eventos: quien publica un resultado no necesita conocer las reacciones de cada observador. Facade simplifica la coordinación de servicios: el componente de reconocimiento no necesita ejecutar directamente cada paso del registro de práctica.
