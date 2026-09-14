from typing import Literal

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


# Define el resultado del reconocimiento
class VisionRespuesta(BaseModel):
    letra: Literal["A", "E", "I", "O", "U"] | None = Field(
        ...,
        description="Vocal reconocida o null si no se reconoce una vocal",
    )

    mensaje: str | None = Field(
        default=None,
        description="Información adicional sobre el resultado",
    )