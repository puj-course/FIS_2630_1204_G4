from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class RegistrarProgresoEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id_letra: int = Field(
        gt=0,
        strict=True,
        description="Identificador de la letra aprendida",
    )


class ActualizarProgresoEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dominada: bool = Field(
        strict=True,
        description="True si está aprendida; False si está en aprendizaje",
    )


class ProgresoRegistrado(BaseModel):
    id_progreso: int
    id_usuario: int
    id_letra: int
    cantidad_intentos: int = Field(ge=0)
    cantidad_aciertos: int = Field(ge=0)
    dominada: bool
    fecha_ultima_practica: datetime | None
    fecha_actualizacion: datetime


class ProgresoRespuesta(BaseModel):
    mensaje: str
    progreso: ProgresoRegistrado

class ProgresoLetraRespuesta(ProgresoRegistrado):
    letra: str = Field(
        description="Letra del alfabeto asociada al progreso",
    )


class ConsultaProgresoRespuesta(BaseModel):
    total: int = Field(
        ge=0,
        description="Cantidad de letras con progreso registrado",
    )
    progresos: list[ProgresoLetraRespuesta]

class EstadoAprendizajeLetraRespuesta(BaseModel):
    id_letra: int = Field(
        gt=0,
        description="Identificador de la letra",
    )
    letra: str = Field(
        description="Letra del alfabeto LSC",
    )
    descripcion: str | None = Field(
        description="Instrucciones de aprendizaje de la letra",
    )
    ruta_imagen: str | None = Field(
        description="Ruta de la imagen de la seña",
    )
    estado: Literal["aprendida", "pendiente"] = Field(
        description=(
            "Aprendida si el progreso tiene dominada=True; "
            "pendiente si tiene dominada=False o no existe progreso"
        ),
    )


class ConsultaEstadoLetrasRespuesta(BaseModel):
    total: int = Field(
        ge=0,
        description="Cantidad de letras disponibles para aprendizaje",
    )
    letras: list[EstadoAprendizajeLetraRespuesta]