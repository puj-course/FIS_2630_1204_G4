import logging

from datetime import datetime, timezone
import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials

from app.limiter import limiter
from app.routes.recuperacion_contrasena import router as router_recuperacion
from app.routes.restablecimiento_contrasena import router as router_restablecimiento
from app.security import (
    ALGORITMO_JWT,
    crear_token_acceso,
    obtener_clave_jwt,
    obtener_usuario_actual,
    revocar_token,
    seguridad_bearer,
)
from app.services.autenticacion_service import CuentaBloqueadaError, autenticar_usuario
from app.services.usuarios_service import CorreoYaRegistradoError, crear_usuario
from src.schemas.autenticacion import CredencialesLogin, TokenRespuesta, UsuarioAutenticadoRespuesta
from src.schemas.usuario import UsuarioAutoRegistro, UsuarioRegistroRespuesta

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)


@router.post("/login", response_model=TokenRespuesta)
@limiter.limit("5/minute")
def iniciar_sesion(request: Request, credenciales: CredencialesLogin):
    try:
        usuario = autenticar_usuario(
            credenciales.correo,
            credenciales.contrasena
        )
    except CuentaBloqueadaError as error:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="La cuenta está bloqueada temporalmente por varios intentos fallidos"
        ) from error

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

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def cerrar_sesion(
    credenciales: HTTPAuthorizationCredentials = Depends(seguridad_bearer),
    _usuario: dict = Depends(obtener_usuario_actual)
):
    contenido = jwt.decode(
        credenciales.credentials,
        obtener_clave_jwt(),
        algorithms=[ALGORITMO_JWT]
    )

    fecha_expiracion = datetime.fromtimestamp(
        contenido["exp"], tz=timezone.utc
    )

    revocar_token(contenido["jti"], fecha_expiracion)

router.include_router(router_recuperacion)
router.include_router(router_restablecimiento)