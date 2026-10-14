from pydantic import BaseModel, Field

from src.schemas.resultados import ResultadoRegistrado
from src.schemas.sesiones import SesionRegistrada


class ResultadoHistorial(ResultadoRegistrado):
    id_usuario: int = Field(gt=0)
    letra_objetivo: str = Field(min_length=1)
    letra_detectada: str = Field(min_length=1)


class SesionHistorial(SesionRegistrada):
    resultados: list[ResultadoHistorial] = Field(
        description="Resultados de la sesión, del más reciente al más antiguo",
    )


class HistorialRespuesta(BaseModel):
    total: int = Field(
        ge=0,
        description="Cantidad de sesiones incluidas en el historial",
    )
    historial: list[SesionHistorial]