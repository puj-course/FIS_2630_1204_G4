from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


# Define la imagen que recibe el endpoint
class VisionEntrada(BaseModel):
    imagen_base64: str = Field(
        ...,
        min_length=1,
        max_length=7_000_000,
        description=(
            "Imagen JPEG o PNG codificada en Base64, "
            "sin el prefijo data:image/...;base64,"
        ),
    )
    id_secuencia: UUID | None = Field(
        default=None,
        description=(
            "Identificador de la secuencia de fotogramas. "
            "Permite analizar movimientos consecutivos."
        ),
    )
    modo: Literal["estatica", "movimiento"] = "estatica"


# Define el resultado del reconocimiento
class VisionRespuesta(BaseModel):
    letra: Literal[
    "A",
    "E",
    "G",
    "H",
    "I",
    "J",
    "Ñ",
    "O",
    "S",
    "U",
    "Z",
] | None = Field(
        ...,
        description="Vocal reconocida o null si no se reconoce una vocal",
    )

    mensaje: str | None = Field(
        default=None,
        description="Letra reconocida o null si no se reconoce una letra",
    )