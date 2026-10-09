import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.security import obtener_usuario_actual
from app.services.historial_service import consultar_historial_usuario
from src.schemas.historial import HistorialRespuesta

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/historial",
    tags=["Historial"],
)


@router.get(
    "",
    response_model=HistorialRespuesta,
    status_code=status.HTTP_200_OK,
    summary="Consultar el historial de reconocimiento del usuario",
    responses={
        200: {
            "description": "Historial consultado correctamente, incluso si está vacío",
        },
        401: {
            "description": (
                "Credenciales ausentes, inválidas, vencidas o revocadas, "
                "o usuario inexistente"
            ),
        },
        500: {
            "description": "No fue posible consultar el historial",
        },
    },
)
def consultar_historial(
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    """Consulta el historial del usuario autenticado.

    - Requiere un token de acceso Bearer.
    - El usuario se obtiene exclusivamente de la autenticación.
    - No requiere cuerpo ni parámetros de consulta.
    - Incluye sesiones activas, finalizadas y canceladas.
    - Ordena sesiones y resultados del más reciente al más antiguo.
    - Incluye sesiones sin resultados.
    - Si no existen sesiones, devuelve total 0 e historial [].
    - total representa la cantidad de sesiones.
    - La consulta no modifica los datos almacenados.
    """
    try:
        historial = consultar_historial_usuario(
            id_usuario=usuario_actual["id_usuario"],
        )

    except Exception as error:
        logger.exception(
            "Error al consultar el historial de reconocimiento"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible consultar el historial",
        ) from error

    return {
        "total": len(historial),
        "historial": historial,
    }