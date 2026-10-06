import os
from pathlib import Path

from dotenv import load_dotenv

RUTA_ENV = Path(__file__).resolve().parent.parent / ".env"
MIN_ACIERTOS_PREDETERMINADO = 3

load_dotenv(RUTA_ENV, override=False)


class ConfiguracionAprendizajeError(ValueError):
    """Indica que la configuración de aprendizaje no es válida."""


def obtener_minimo_aciertos() -> int:
    """Obtiene la cantidad mínima de aciertos para aprender una letra."""

    valor = os.getenv(
        "APRENDIZAJE_MIN_ACIERTOS",
        str(MIN_ACIERTOS_PREDETERMINADO),
    )

    try:
        minimo = int(valor)
    except ValueError as error:
        raise ConfiguracionAprendizajeError(
            "APRENDIZAJE_MIN_ACIERTOS debe ser un entero mayor que cero"
        ) from error

    if minimo <= 0:
        raise ConfiguracionAprendizajeError(
            "APRENDIZAJE_MIN_ACIERTOS debe ser un entero mayor que cero"
        )

    return minimo