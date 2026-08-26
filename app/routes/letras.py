import logging

from fastapi import APIRouter, HTTPException

from app.services.letras_service import obtener_letras_registradas
from src.schemas.letra import LetraRespuesta


logger = logging.getLogger(__name__)

router = APIRouter(tags=["Letras"])


@router.get("/letras", response_model=list[LetraRespuesta])
def consultar_letras():
    try:
        return obtener_letras_registradas()

    except Exception as error:
        logger.exception(
            "Ocurrió un error al consultar las letras"
        )

        raise HTTPException(
            status_code=500,
            detail="No fue posible consultar las letras"
        ) from error