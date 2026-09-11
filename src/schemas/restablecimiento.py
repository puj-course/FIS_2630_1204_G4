import re

from pydantic import (
    BaseModel, ConfigDict, Field, SecretStr, field_validator, model_validator
)


class SolicitudRestablecimiento(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)

    token: SecretStr = Field(min_length=43, max_length=43)
    nueva_contrasena: SecretStr = Field(min_length=12, max_length=200)
    confirmacion_contrasena: SecretStr = Field(min_length=12, max_length=200)

    @field_validator("token")
    @classmethod
    def validar_token(cls, valor: SecretStr) -> SecretStr:
        if not re.fullmatch(r"[A-Za-z0-9_-]{43}", valor.get_secret_value()):
            raise ValueError("El token de recuperación no tiene un formato válido")
        return valor

    @model_validator(mode="after")
    def validar_confirmacion(self):
        if (
            self.nueva_contrasena.get_secret_value()
            != self.confirmacion_contrasena.get_secret_value()
        ):
            raise ValueError("Las contraseñas no coinciden")
        return self


class RespuestaRestablecimiento(BaseModel):
    mensaje: str
