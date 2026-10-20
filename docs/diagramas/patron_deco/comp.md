flowchart LR
    VS["vision_service.py"] -->|"reconocer_mano()"| REC["reconocimiento.py"]
    REC -->|"crea y envuelve la estrategia"| DEC["decoradores_reconocimiento.py"]
    REC -.->|"utiliza contrato"| ESTR["estrategia_reconocimiento.py"]
    DEC -.->|"implementa contrato"| ESTR
    DEC -->|"mide duración"| TIME["time.perf_counter()"]
    DEC -->|"registra métricas"| LOG["logging"]