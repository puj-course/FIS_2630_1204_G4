import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.security import obtener_usuario_actual
from app.services.intentos_service import consultar_intentos_usuario
from src.schemas.intentos import IntentosConsultaRespuesta

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/intentos",
    tags=["Intentos"],
)


@router.get(
    "",
    response_model=IntentosConsultaRespuesta,
    status_code=status.HTTP_200_OK,
    summary="Consultar intentos del usuario autenticado",
    responses={
        200: {
            "description": "Intentos consultados correctamente",
        },
        401: {
            "description": "Credenciales ausentes o inválidas",
        },
        422: {
            "description": "Los filtros deben ser enteros positivos",
        },
        500: {
            "description": "No fue posible consultar los intentos",
        },
    },
)
def obtener_intentos(
    id_letra: int | None = Query(
        default=None,
        gt=0,
        description="Filtrar por el identificador de la letra objetivo",
    ),
    id_sesion: int | None = Query(
        default=None,
        gt=0,
        description="Filtrar por el identificador de la sesión",
    ),
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    """
    Consulta únicamente los intentos del usuario autenticado.

    - Requiere un token de acceso Bearer.
    - Sin filtros, devuelve todos sus intentos.
    - Permite filtrar por letra objetivo, sesión o ambos.
    - Si se envían ambos filtros, se aplican conjuntamente.
    - Ordena del intento más reciente al más antiguo.
    - Sin coincidencias, devuelve total 0 e intentos [].
    - Una sesión ajena o inexistente devuelve una lista vacía.
    - Permite consultar intentos de sesiones ya finalizadas.

    El identificador del usuario se obtiene de la autenticación.
    """

    try:
        intentos = consultar_intentos_usuario(
            id_usuario=usuario_actual["id_usuario"],
            id_letra=id_letra,
            id_sesion=id_sesion,
        )

    except Exception as error:
        logger.exception(
            "Error al consultar los intentos del usuario"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible consultar los intentos",
        ) from error

    return {
        "total": len(intentos),
        "intentos": intentos,
    }