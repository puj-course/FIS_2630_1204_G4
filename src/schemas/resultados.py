from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RegistrarResultadoEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id_sesion: int = Field(
        gt=0,
        strict=True,
        description="Identificador de la sesión de reconocimiento",
    )

    id_letra_objetivo: int = Field(
        gt=0,
        strict=True,
        description="Letra que el usuario intenta realizar",
    )

    id_letra_detectada: int = Field(
        gt=0,
        strict=True,
        description="Letra detectada por el módulo visual",
    )

    confianza: float = Field(
        ge=0,
        le=1,
        description="Nivel de confianza del reconocimiento",
    )


class ResultadoRegistrado(BaseModel):
    id_resultado: int
    id_sesion: int
    id_letra_objetivo: int
    id_letra_detectada: int
    confianza: float
    es_correcto: bool
    fecha_resultado: datetime


class ResultadoRespuesta(BaseModel):
    mensaje: str
    resultado: ResultadoRegistrado