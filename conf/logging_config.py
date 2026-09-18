import logging
import os

# los archivos de rutas usan logging.getLogger(__name__) para poder
# registrar sus propios mensajes, pero no necesitan configurar nada aparte:
# todos van a terminar usando el formato que se define aqui abajo

def configurar_logging() -> None:
    nivel = os.getenv("LOG_LEVEL", "INFO").upper()

    logging.basicConfig(
        level=nivel,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",

    )