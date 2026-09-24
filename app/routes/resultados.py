import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.security import obtener_usuario_actual
from app.services.resultados_service import (
    LetraNoEncontradaError,
    SesionNoEncontradaError,
    UsuarioSesionError,
    registrar_resultado,
)
from src.schemas.resultados import (
    RegistrarResultadoEntrada,
    ResultadoRespuesta,
)

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/resultados",
    tags=["Resultados"],
)


@router.post(
    "",
    response_model=ResultadoRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear_resultado(
    datos: RegistrarResultadoEntrada,
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    """
    Registra un resultado generado durante una sesión
    de reconocimiento visual.
    """

    try:
        resultado = registrar_resultado(
            id_usuario=usuario_actual["id_usuario"],
            id_sesion=datos.id_sesion,
            id_letra_objetivo=datos.id_letra_objetivo,
            id_letra_detectada=datos.id_letra_detectada,
            confianza=datos.confianza,
        )

        return {
            "mensaje": "Resultado registrado correctamente",
            "resultado": resultado,
        }

    except SesionNoEncontradaError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error


    except UsuarioSesionError as error:
        raise HTTPException(
            status_code=403,
            detail=str(error),
        ) from error


    except LetraNoEncontradaError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error


    except Exception as error:
        logger.exception(
            "Error registrando resultado de reconocimiento"
        )

        raise HTTPException(
            status_code=500,
            detail="No fue posible registrar el resultado",
        ) from error