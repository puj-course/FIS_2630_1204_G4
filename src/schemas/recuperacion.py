from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator
)


class SolicitudRecuperacion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    correo: EmailStr = Field(min_length=5, max_length=150)

    # Se elimina el espacio externo y se conserva el uso de minúsculas
    @field_validator("correo", mode="before")
    @classmethod
    def normalizar_correo(cls, valor):
        if isinstance(valor, str):
            return valor.strip().lower()

        return valor


class RespuestaRecuperacion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mensaje: str
