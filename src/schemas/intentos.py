from datetime import datetime

from pydantic import BaseModel, Field


class IntentoRegistrado(BaseModel):
    id_intento: int = Field(
        gt=0,
        description="Identificador del intento",
    )

    id_resultado: int = Field(
        gt=0,
        description="Resultado de reconocimiento asociado",
    )

    id_usuario: int = Field(
        gt=0,
        description="Usuario que realizó el intento",
    )

    id_sesion: int = Field(
        gt=0,
        description="Sesión en la que se realizó el intento",
    )

    id_letra: int = Field(
        gt=0,
        description="Letra objetivo que practicaba el usuario",
    )

    es_correcto: bool = Field(
        strict=True,
        description="Indica si la letra detectada coincide con la objetivo",
    )

    fecha_intento: datetime = Field(
        description="Fecha y hora en que se registró el intento",
    )


class IntentosConsultaRespuesta(BaseModel):
    total: int = Field(
        ge=0,
        description="Cantidad de intentos devueltos por la consulta",
    )

    intentos: list[IntentoRegistrado] = Field(
        description="Intentos que cumplen los filtros de la consulta",
    )