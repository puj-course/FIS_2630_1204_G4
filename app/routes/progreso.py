import logging

from fastapi import APIRouter, Depends, HTTPException, Path

from app.security import obtener_usuario_actual
from app.services.progreso_service import (
    LetraNoEncontradaError,
    ProgresoNoEncontradoError,
    UsuarioNoEncontradoError,
    actualizar_estado_progreso,
    consultar_estado_letras_usuario,
    consultar_progreso_usuario,
    registrar_progreso,
)
from src.schemas.progreso import (
    ActualizarProgresoEntrada,
    ConsultaEstadoLetrasRespuesta,
    ConsultaProgresoRespuesta,
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

@router.get(
    "/letras",
    response_model=ConsultaEstadoLetrasRespuesta,
    status_code=200,
    summary="Consultar el estado de aprendizaje de las letras",
    responses={
        401: {"description": "El usuario no está autenticado"},
        500: {
            "description": (
                "No fue posible consultar el estado de las letras"
            ),
        },
    },
)
def consultar_estado_mis_letras(
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    """
    Devuelve todas las letras activas con el estado del usuario del token.

    - Aprendida: tiene un registro con dominada=True.
    - Pendiente: tiene dominada=False o no tiene progreso registrado.
    - Si no hay letras activas, devuelve una lista vacía.
    """

    try:
        letras = consultar_estado_letras_usuario(
            id_usuario=usuario_actual["id_usuario"],
        )

    except Exception as error:
        logger.exception(
            "Ocurrió un error al consultar el estado de las letras"
        )

        raise HTTPException(
            status_code=500,
            detail="No fue posible consultar el estado de las letras",
        ) from error

    return {
        "total": len(letras),
        "letras": letras,
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

@router.get(
    "",
    response_model=ConsultaProgresoRespuesta,
    status_code=200,
    summary="Consultar el progreso del usuario autenticado",
    responses={
        401: {"description": "El usuario no está autenticado"},
        500: {"description": "No fue posible consultar el progreso"},
    },
)
def consultar_mi_progreso(
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    """
    Devuelve las letras con progreso registrado para el usuario del token.

    Incluye el estado de aprendizaje, los contadores y las fechas.
    Si no tiene progreso registrado, devuelve una lista vacía.
    """

    try:
        progresos = consultar_progreso_usuario(
            id_usuario=usuario_actual["id_usuario"],
        )

    except Exception as error:
        logger.exception(
            "Ocurrió un error al consultar el progreso"
        )

        raise HTTPException(
            status_code=500,
            detail="No fue posible consultar el progreso",
        ) from error

    return {
        "total": len(progresos),
        "progresos": progresos,
    }