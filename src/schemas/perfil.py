from pydantic import BaseModel, Field

from src.schemas.autenticacion import UsuarioAutenticadoRespuesta


class ProgresoPerfilRespuesta(BaseModel):
    total_letras: int = Field(ge=0)
    letras_iniciadas: int = Field(ge=0)
    letras_dominadas: int = Field(ge=0)
    cantidad_intentos: int = Field(ge=0)
    cantidad_aciertos: int = Field(ge=0)
    porcentaje_progreso: float = Field(ge=0, le=100)


class PerfilRespuesta(UsuarioAutenticadoRespuesta):
    progreso: ProgresoPerfilRespuesta