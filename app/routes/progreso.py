import logging

from fastapi import APIRouter, Depends, HTTPException, Path

from app.security import obtener_usuario_actual
from app.services.progreso_service import (
    LetraNoEncontradaError,
    ProgresoNoEncontradoError,
    UsuarioNoEncontradoError,
    actualizar_estado_progreso,
    registrar_progreso,
)
from src.schemas.progreso import (
    ActualizarProgresoEntrada,
    ProgresoRespuesta,
    RegistrarProgresoEntrada,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/progreso",
    tags=["Progreso"],
)


@router.post(
    "",
    response_model=ProgresoRespuesta,
    status_code=200,
    summary="Registrar una letra aprendida",
    responses={
        401: {"description": "El usuario no está autenticado"},
        404: {"description": "El usuario o la letra no existe"},
        422: {"description": "Los datos enviados no son válidos"},
        500: {"description": "No fue posible registrar el progreso"},
    },
)
def registrar_letra_aprendida(
    datos: RegistrarProgresoEntrada,
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    """
    Registra una letra como aprendida para el usuario del token.

    Si el progreso ya existe, lo marca como aprendido sin duplicarlo.
    Conserva los contadores y la fecha de última práctica.
    """

    try:
        progreso = registrar_progreso(
            id_usuario=usuario_actual["id_usuario"],
            id_letra=datos.id_letra,
        )

    except (
        UsuarioNoEncontradoError,
        LetraNoEncontradaError,
    ) as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception(
            "Ocurrió un error al registrar el progreso"
        )

        raise HTTPException(
            status_code=500,
            detail="No fue posible registrar el progreso",
        ) from error

    return {
        "mensaje": "Letra registrada como aprendida",
        "progreso": progreso,
    }


@router.patch(
    "/{id_letra}",
    response_model=ProgresoRespuesta,
    status_code=200,
    summary="Actualizar el estado de aprendizaje de una letra",
    responses={
        401: {"description": "El usuario no está autenticado"},
        404: {"description": "No existe progreso para el usuario y la letra"},
        422: {"description": "Los datos enviados no son válidos"},
        500: {"description": "No fue posible actualizar el progreso"},
    },
)
def actualizar_progreso_letra(
    datos: ActualizarProgresoEntrada,
    id_letra: int = Path(
        gt=0,
        description="Identificador de la letra",
    ),
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    """
    Actualiza únicamente el progreso del usuario del token.

    - True: letra aprendida.
    - False: letra en aprendizaje.
    - Si no existe el progreso, devuelve 404.
    """

    try:
        progreso = actualizar_estado_progreso(
            id_usuario=usuario_actual["id_usuario"],
            id_letra=id_letra,
            dominada=datos.dominada,
        )

    except ProgresoNoEncontradoError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception(
            "Ocurrió un error al actualizar el progreso"
        )

        raise HTTPException(
            status_code=500,
            detail="No fue posible actualizar el progreso",
        ) from error

    return {
        "mensaje": "Estado de aprendizaje actualizado correctamente",
        "progreso": progreso,
    }