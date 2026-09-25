import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.security import crear_error_credenciales, obtener_usuario_actual
from app.services.sesiones_service import (
    EstadoSesionError,
    SesionNoEncontradaError,
    UsuarioNoEncontradoError,
    crear_sesion,
    finalizar_sesion,
)
from src.schemas.sesiones import SesionRespuesta
from src.schemas.sesiones import (
    FinalizarSesionRespuesta,
    SesionRespuesta,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Sesiones de reconocimiento"],
)


@router.post(
    "/sesiones",
    response_model=SesionRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Iniciar una sesión de reconocimiento",
    responses={
        401: {
            "description": "Credenciales ausentes, inválidas o usuario inexistente",
        },
        500: {
            "description": "No fue posible iniciar la sesión",
        },
    },
)
def iniciar_sesion(
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    """
    Crea una sesión activa para el usuario autenticado.

    - Requiere un token de acceso Bearer.
    - No requiere cuerpo de solicitud.
    - El usuario se obtiene exclusivamente del token.
    - PostgreSQL asigna la fecha y hora de inicio.
    - Devuelve el identificador de la sesión para asociar resultados.
    """

    try:
        sesion = crear_sesion(
            id_usuario=usuario_actual["id_usuario"],
        )

    except UsuarioNoEncontradoError as error:
        # Controla que el usuario haya sido eliminado después
        # de validar el token y antes de crear la sesión.
        raise crear_error_credenciales() from error

    except Exception as error:
        logger.exception(
            "Ocurrió un error al iniciar la sesión de reconocimiento"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible iniciar la sesión de reconocimiento",
        ) from error

    return {
        "mensaje": "Sesión de reconocimiento iniciada correctamente",
        "sesion": sesion,
    }

@router.patch(
    "/sesiones/{id_sesion}/finalizar",
    response_model=FinalizarSesionRespuesta,
    status_code=status.HTTP_200_OK,
    summary="Finalizar una sesión de reconocimiento",
    responses={
        401: {
            "description": "Usuario no autenticado",
        },
        404: {
            "description": "La sesión no existe o no pertenece al usuario",
        },
        409: {
            "description": "La sesión no puede finalizarse",
        },
        500: {
            "description": "No fue posible finalizar la sesión",
        },
    },
)
def cerrar_sesion(
    id_sesion: int,
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    """
    Finaliza una sesión de reconocimiento del usuario autenticado.

    - Verifica que la sesión pertenezca al usuario.
    - Cambia el estado a finalizada.
    - Registra la fecha de finalización.
    """

    try:
        sesion = finalizar_sesion(
            id_usuario=usuario_actual["id_usuario"],
            id_sesion=id_sesion,
        )

    except SesionNoEncontradaError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except EstadoSesionError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception(
            "Ocurrió un error al finalizar la sesión"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible finalizar la sesión",
        ) from error

    return {
        "mensaje": "Sesión finalizada correctamente",
        "sesion": sesion,
    }