classDiagram
    direction TB

    class EstrategiaReconocimiento {
        <<abstract>>
        +reconocer(mano, fotogramas=()) dict
    }

    class ReconocimientoEstatico {
        +reconocer(mano, fotogramas=()) dict
    }

    class ReconocimientoMovimiento {
        +reconocer(mano, fotogramas=()) dict
    }

    class DecoradorReconocimiento {
        <<abstract>>
        #_estrategia: EstrategiaReconocimiento
        +__init__(estrategia)
        +reconocer(mano, fotogramas=()) dict
    }

    class DecoradorMedicionTiempo {
        +reconocer(mano, fotogramas=()) dict
    }

    class ReconocedorMano {
        -_estrategia: EstrategiaReconocimiento
        +__init__(estrategia)
        +cambiar_estrategia(estrategia) None
        +reconocer(mano, fotogramas=()) dict
    }

    EstrategiaReconocimiento <|-- ReconocimientoEstatico
    EstrategiaReconocimiento <|-- ReconocimientoMovimiento
    EstrategiaReconocimiento <|-- DecoradorReconocimiento
    DecoradorReconocimiento <|-- DecoradorMedicionTiempo

    DecoradorReconocimiento o-- EstrategiaReconocimiento : envuelve
    ReconocedorMano --> EstrategiaReconocimiento : usa