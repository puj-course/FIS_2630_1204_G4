import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.security import obtener_usuario_actual
from app.services.resultados_reconocimiento_service import (
    LetraDetectadaNoEncontradaError,
    LetraObjetivoNoEncontradaError,
    obtener_resultados_usuario,
    registrar_resultado_reconocimiento,
)
from src.schemas.resultado_reconocimiento import (
    ResultadoReconocimientoEntrada,
    ResultadoReconocimientoRespuesta,
    ResultadosReconocimientoConsultaRespuesta,
)

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/resultados-reconocimiento",
    tags=["Resultados de reconocimiento"],
)

@router.get(
    "",
    response_model=ResultadosReconocimientoConsultaRespuesta,
    status_code=status.HTTP_200_OK,
    summary="Consultar resultados de reconocimiento",
    responses={
        401: {
            "description": "El usuario no está autenticado",
        },
        500: {
            "description": "No fue posible consultar los resultados",
        },
    },
)
def consultar_resultados(
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    """
    Recupera los resultados del usuario autenticado.

    - Obtiene el usuario desde el token.
    - Consulta únicamente las sesiones pertenecientes al usuario.
    - Devuelve una lista vacía cuando no existen resultados.
    """

    try:
        resultados = obtener_resultados_usuario(
            id_usuario=usuario_actual["id_usuario"]
        )

    except Exception as error:
        logger.exception(
            "Ocurrió un error al consultar los resultados"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible consultar los resultados",
        ) from error

    return {
        "total": len(resultados),
        "resultados": resultados,
    }
@router.post(
    "",
    response_model=ResultadoReconocimientoRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un resultado de reconocimiento",
    responses={
        401: {
            "description": "El usuario no está autenticado",
        },
        404: {
            "description": "La letra objetivo o detectada no existe",
        },
        422: {
            "description": "Los datos enviados no son válidos",
        },
        500: {
            "description": "No fue posible registrar el resultado",
        },
    },
)
def registrar_resultado(
    datos: ResultadoReconocimientoEntrada,
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    """
    Registra un intento de práctica del usuario autenticado.

    - Crea una sesión de reconocimiento para el intento.
    - Relaciona la sesión con el usuario del token.
    - Guarda la letra objetivo y la letra detectada.
    - Calcula si el reconocimiento fue correcto.
    - Devuelve los datos almacenados.
    """

    try:
        resultado = registrar_resultado_reconocimiento(
            id_usuario=usuario_actual["id_usuario"],
            id_letra_objetivo=datos.id_letra_objetivo,
            letra_detectada=datos.letra_detectada,
            confianza=datos.confianza,
        )

    except (
        LetraObjetivoNoEncontradaError,
        LetraDetectadaNoEncontradaError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception(
            "Ocurrió un error al registrar el resultado"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible registrar el resultado",
        ) from error

    return {
        "mensaje": "Resultado registrado correctamente",
        "resultado": resultado,
    }