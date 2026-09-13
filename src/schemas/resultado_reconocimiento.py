from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ResultadoReconocimientoEntrada(BaseModel):
    id_letra_objetivo: int = Field(
        gt=0,
        description="Identificador de la letra que practica el usuario"
    )

    letra_detectada: str = Field(
        min_length=1,
        max_length=2,
        description="Letra reconocida por el módulo visual"
    )

    confianza: float = Field(
        ge=0,
        le=1,
        description="Nivel de confianza del reconocimiento"
    )

    @field_validator("letra_detectada", mode="before")
    @classmethod
    def normalizar_letra(cls, valor):
        if isinstance(valor, str):
            return valor.strip().upper()

        return valor


class ResultadoRegistrado(BaseModel):
    id_resultado: int
    id_sesion: int
    id_usuario: int

    id_letra_objetivo: int
    letra_objetivo: str

    id_letra_detectada: int
    letra_detectada: str

    confianza: float = Field(ge=0, le=1)
    es_correcto: bool
    fecha_resultado: datetime


class ResultadoReconocimientoRespuesta(BaseModel):
    mensaje: str
    resultado: ResultadoRegistrado


class ResultadosReconocimientoConsultaRespuesta(BaseModel):
    total: int = Field(
        ge=0,
        description="Cantidad de resultados encontrados"
    )

    resultados: list[ResultadoRegistrado]