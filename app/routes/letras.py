import logging

from fastapi import APIRouter, Depends, HTTPException
from app.security import requerir_administrador
from app.services.letras_service import (
    actualizar_informacion_letra,
    obtener_letra_por_id,
    obtener_letras_registradas
)
from src.schemas.letra import (
    LetraActualizacion,
    LetraActualizacionRespuesta,
    LetraRespuesta
)


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


@router.get("/letras/{id_letra}", response_model=LetraRespuesta)
def consultar_letra(id_letra: int):
    try:
        letra = obtener_letra_por_id(id_letra)

    except Exception as error:
        logger.exception(
            "Ocurrió un error al consultar la letra"
        )

        raise HTTPException(
            status_code=500,
            detail="No fue posible consultar la letra"
        ) from error

    if letra is None:
        raise HTTPException(
            status_code=404,
            detail="La letra solicitada no existe"
        )

    return letra

@router.patch(
    "/letras/{id_letra}",
    response_model=LetraActualizacionRespuesta
)
def actualizar_letra(
    id_letra: int,
    datos: LetraActualizacion,
    _administrador: dict = Depends(requerir_administrador)
):
    cambios = datos.model_dump(exclude_unset=True)

    if not cambios:
        raise HTTPException(
            status_code=400,
            detail="Debe enviar al menos un campo para actualizar"
        )

    try:
        letra_actualizada = actualizar_informacion_letra(
            id_letra,
            cambios
        )

    except Exception as error:
        logger.exception(
            "Ocurrió un error al actualizar la letra"
        )

        raise HTTPException(
            status_code=500,
            detail="No fue posible actualizar la letra"
        ) from error

    if letra_actualizada is None:
        raise HTTPException(
            status_code=404,
            detail="La letra solicitada no existe"
        )

    return {
        "mensaje": "La letra fue actualizada correctamente",
        "letra": letra_actualizada
    }