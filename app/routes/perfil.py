import logging

from fastapi import APIRouter, Depends, HTTPException

from app.security import obtener_usuario_actual
from app.services.perfil_service import obtener_progreso_usuario
from src.schemas.perfil import PerfilRespuesta


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/perfil",
    tags=["Perfil"]
)


@router.get("", response_model=PerfilRespuesta)
def consultar_perfil(
    usuario_actual: dict = Depends(obtener_usuario_actual)
):
    try:
        progreso = obtener_progreso_usuario(
            usuario_actual["id_usuario"]
        )

    except Exception as error:
        logger.exception(
            "Ocurrió un error al consultar el perfil"
        )

        raise HTTPException(
            status_code=500,
            detail="No fue posible consultar el perfil"
        ) from error

    return {
        "id_usuario": usuario_actual["id_usuario"],
        "nombre": usuario_actual["nombre"],
        "correo": usuario_actual["correo"],
        "rol": usuario_actual["rol"],
        "progreso": progreso
    }