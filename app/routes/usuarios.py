import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.security import requerir_administrador
from app.services.usuarios_service import (
    CorreoYaRegistradoError,
    crear_usuario
)
from src.schemas.usuario import (
    UsuarioRegistro,
    UsuarioRegistroRespuesta
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)


@router.post(
    "",
    response_model=UsuarioRegistroRespuesta,
    status_code=status.HTTP_201_CREATED
)
def registrar_usuario(
    datos: UsuarioRegistro,
    _administrador: dict = Depends(requerir_administrador)
):
    try:
        usuario = crear_usuario(
            nombre=datos.nombre,
            correo=datos.correo,
            contrasena=datos.contrasena,
            rol=datos.rol
        )

    except CorreoYaRegistradoError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo ya se encuentra registrado"
        ) from error

    except Exception as error:
        logger.exception(
            "Ocurrió un error al registrar el usuario"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible registrar el usuario"
        ) from error

    return {
        "mensaje": "Usuario registrado correctamente",
        "usuario": usuario
    }