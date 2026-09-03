from pydantic import BaseModel, field_validator


class LetraRespuesta(BaseModel):
    id_letra: int
    letra: str
    descripcion: str | None = None
    ruta_imagen: str | None = None

class LetraActualizacion(BaseModel):
    descripcion: str | None = None
    ruta_imagen: str | None = None

    @field_validator("descripcion", "ruta_imagen")
    @classmethod
    def validar_campo_no_vacio(cls, valor):
        if valor is None or not valor.strip():
            raise ValueError(
                "El campo enviado no puede estar vacío"
            )

        return valor.strip()


class LetraActualizacionRespuesta(BaseModel):
    mensaje: str
    letra: LetraRespuesta