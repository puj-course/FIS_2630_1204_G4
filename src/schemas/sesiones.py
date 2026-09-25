from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SesionRegistrada(BaseModel):
    id_sesion: int = Field(gt=0)
    id_usuario: int = Field(gt=0)
    fecha_inicio: datetime
    fecha_fin: datetime | None
    estado: Literal["activa", "finalizada", "cancelada"]


class SesionRespuesta(BaseModel):
    mensaje: str = Field(min_length=1)
    sesion: SesionRegistrada


class FinalizarSesionRespuesta(BaseModel):
    mensaje: str = Field(min_length=1)
    sesion: SesionRegistrada