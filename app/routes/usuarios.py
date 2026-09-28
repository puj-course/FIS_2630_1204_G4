import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.security import requerir_administrador
from app.services.usuarios_service import (
    CorreoYaRegistradoError,
    cambiar_rol,
    crear_usuario,
    desactivar_usuario,
    listar_usuarios,
)
from src.schemas.usuario import (
    CambioRolUsuario,
    UsuarioDesactivadoRespuesta,
    UsuarioListado,
    UsuarioRegistro,
    UsuarioRegistroRespuesta,
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

@router.get(
    "",
    response_model=list[UsuarioListado]
)
def obtener_usuarios(
    buscar: str | None = None,
    _administrador: dict = Depends(requerir_administrador)
):
    try:
        return listar_usuarios(buscar)
    
    except Exception as error:
        logger.exception(
            "Ocurrió un error al listar usuarios"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible obtener la lista de los usuarios"
        ) from error


@router.patch(
    "/{id_usuario}/rol",
    response_model=UsuarioListado
)
def actualizar_rol(
    id_usuario: int,
    datos: CambioRolUsuario,
    administrador: dict = Depends(requerir_administrador)
):
    if id_usuario == administrador["id_usuario"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede cambiar su propio rol"
        )
    usuario = cambiar_rol(id_usuario, datos.nuevo_rol)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario no existe"
        )

    return usuario

@router.patch(
    "/{id_usuario}/desactivar",
    response_model=UsuarioDesactivadoRespuesta
)
def desactivar(
    id_usuario: int,
    administrador: dict = Depends(requerir_administrador)
):
    if id_usuario == administrador["id_usuario"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede desactivar su propia cuenta"
        )
    usuario = desactivar_usuario(id_usuario)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario no existe"
        )

    return usuario