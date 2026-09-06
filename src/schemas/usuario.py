from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator
)

from src.schemas.autenticacion import UsuarioAutenticadoRespuesta


class DatosRegistroUsuario(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str = Field(min_length=2, max_length=100)
    correo: str = Field(min_length=5, max_length=150)
    contrasena: str = Field(min_length=12, max_length=200)

    @field_validator("nombre", "correo", mode="before")
    @classmethod
    def eliminar_espacios_externos(cls, valor):
        if isinstance(valor, str):
            return valor.strip()

        return valor

    @field_validator("correo")
    @classmethod
    def normalizar_correo(cls, correo):
        return correo.lower()


class UsuarioAutoRegistro(DatosRegistroUsuario):
    pass


class UsuarioRegistro(DatosRegistroUsuario):
    rol: Literal["usuario", "administrador"] = "usuario"


class UsuarioRegistroRespuesta(BaseModel):
    mensaje: str
    usuario: UsuarioAutenticadoRespuesta