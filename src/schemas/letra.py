from pydantic import BaseModel


class LetraRespuesta(BaseModel):
    id_letra: int
    letra: str
    descripcion: str | None = None
    ruta_imagen: str | None = None