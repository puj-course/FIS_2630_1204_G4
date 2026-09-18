import logging
import os

def configurar_logging() -> None:
    nivel = os.getenv("LOG_LEVEL", "INFO").upper()

    logging.basicConfig(
        level=nivel,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",

    )