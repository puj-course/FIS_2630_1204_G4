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
        description="Identificador de la letra que practica el usuario",
    )

    id_letra_detectada: int = Field(
        gt=0,
        strict=True,
        description="Identificador de la letra detectada",
    )

    confianza: float = Field(
        ge=0,
        le=1,
        strict=True,
        allow_inf_nan=False,
        description="Nivel de confianza entre 0 y 1",
    )


class ResultadoRegistrado(BaseModel):
    id_resultado: int = Field(gt=0)
    id_sesion: int = Field(gt=0)
    id_letra_objetivo: int = Field(gt=0)
    id_letra_detectada: int = Field(gt=0)

    confianza: float = Field(
        ge=0,
        le=1,
        allow_inf_nan=False,
    )

    es_correcto: bool = Field(strict=True)
    fecha_resultado: datetime


class ResultadoRespuesta(BaseModel):
    mensaje: str = Field(min_length=1)
    resultado: ResultadoRegistrado


class ResultadosConsultaRespuesta(BaseModel):
    total: int = Field(ge=0)
    resultados: list[ResultadoRegistrado]