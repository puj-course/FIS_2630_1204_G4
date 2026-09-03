import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.security import crear_token_acceso, obtener_usuario_actual
from app.services.autenticacion_service import autenticar_usuario
from src.schemas.autenticacion import (
    CredencialesLogin,
    TokenRespuesta,
    UsuarioAutenticadoRespuesta
)
from app.services.usuarios_service import (
    CorreoYaRegistradoError,
    crear_usuario
)
from src.schemas.usuario import (
    UsuarioAutoRegistro,
    UsuarioRegistroRespuesta
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)


@router.post("/login", response_model=TokenRespuesta)
def iniciar_sesion(credenciales: CredencialesLogin):
    try:
        usuario = autenticar_usuario(
            credenciales.correo,
            credenciales.contrasena
        )

    except Exception as error:
        logger.exception(
            "Ocurrió un error durante la autenticación"
        )

        raise HTTPException(
            status_code=500,
            detail="No fue posible iniciar sesión"
        ) from error

    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        token = crear_token_acceso(usuario["id_usuario"])

    except Exception as error:
        logger.exception(
            "Ocurrió un error al generar el token"
        )

        raise HTTPException(
            status_code=500,
            detail="No fue posible iniciar sesión"
        ) from error

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": usuario
    }


@router.get(
    "/me",
    response_model=UsuarioAutenticadoRespuesta
)
def consultar_usuario_actual(
    usuario=Depends(obtener_usuario_actual)
):
    return usuario

@router.post(
    "/registro",
    response_model=UsuarioRegistroRespuesta,
    status_code=status.HTTP_201_CREATED
)
def autorregistrar_usuario(datos: UsuarioAutoRegistro):
    try:
        usuario = crear_usuario(
            nombre=datos.nombre,
            correo=datos.correo,
            contrasena=datos.contrasena,
            rol="usuario"
        )

    except CorreoYaRegistradoError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo ya se encuentra registrado"
        ) from error

    except Exception as error:
        logger.exception(
            "Ocurrió un error durante el autorregistro"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible registrar el usuario"
        ) from error

    return {
        "mensaje": "Usuario registrado correctamente",
        "usuario": usuario
    }