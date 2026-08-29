from pydantic import BaseModel, Field


class CredencialesLogin(BaseModel):
    correo: str = Field(min_length=3, max_length=150)
    contrasena: str = Field(min_length=1, max_length=200)


class UsuarioAutenticadoRespuesta(BaseModel):
    id_usuario: int
    nombre: str
    correo: str
    rol: str


class TokenRespuesta(BaseModel):
    access_token: str
    token_type: str
    usuario: UsuarioAutenticadoRespuesta