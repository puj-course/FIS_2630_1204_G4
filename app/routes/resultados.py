import logging

from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.security import obtener_usuario_actual
from app.services.resultados_service import (
    LetraNoEncontradaError,
    SesionNoEncontradaError,
    UsuarioSesionError,
    consultar_resultados_sesion,
    registrar_resultado,
)
from src.schemas.resultados import (
    RegistrarResultadoEntrada,
    ResultadoRespuesta,
    ResultadosConsultaRespuesta,
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
    summary="Registrar un resultado de reconocimiento en una sesión",
    responses={
        201: {
            "description": "Resultado registrado correctamente",
        },
        401: {
            "description": "Credenciales ausentes o inválidas",
        },
        403: {
            "description": "La sesión pertenece a otro usuario",
        },
        404: {
            "description": "La sesión o alguna de las letras no existe",
        },
        422: {
            "description": "Los datos enviados no cumplen el esquema",
        },
        500: {
            "description": "No fue posible registrar el resultado",
        },
    },
)
def crear_resultado(
    datos: RegistrarResultadoEntrada,
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    """
    Registra un resultado dentro de una sesión del usuario autenticado.

    Requiere un token de acceso Bearer.

    El cuerpo debe incluir:
    - id_sesion: identificador de una sesión propia.
    - id_letra_objetivo: identificador de la letra practicada.
    - id_letra_detectada: identificador de la letra reconocida.
    - confianza: número entre 0 y 1.

    Los identificadores deben ser enteros positivos.
    No se admiten campos adicionales.

    El usuario se obtiene del token. El servicio calcula es_correcto
    comparando las letras y PostgreSQL asigna la fecha del resultado.

    Devuelve el resultado almacenado y su identificador.
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

@router.get(
    "/sesion/{id_sesion}",
    response_model=ResultadosConsultaRespuesta,
    status_code=status.HTTP_200_OK,
    summary="Consultar resultados de una sesión propia",
    responses={
        401: {
            "description": "Credenciales ausentes o inválidas",
        },
        403: {
            "description": "La sesión pertenece a otro usuario",
        },
        404: {
            "description": "La sesión no existe",
        },
        422: {
            "description": "El identificador de sesión no es válido",
        },
        500: {
            "description": "No fue posible consultar los resultados",
        },
    },
)
def obtener_resultados_de_sesion(
    id_sesion: int = Path(
        gt=0,
        description="Identificador de la sesión que se desea consultar",
    ),
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    """
    Consulta los resultados de una sesión del usuario autenticado.

    - Requiere un token de acceso Bearer.
    - Verifica que la sesión exista y pertenezca al usuario.
    - Devuelve los resultados ordenados del más antiguo al más reciente.
    - Una sesión sin resultados devuelve total 0 y una lista vacía.
    - Permite consultar sesiones activas, finalizadas o canceladas.
    """

    try:
        resultados = consultar_resultados_sesion(
            id_usuario=usuario_actual["id_usuario"],
            id_sesion=id_sesion,
        )

    except SesionNoEncontradaError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except UsuarioSesionError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception(
            "Error al consultar resultados de una sesión"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible consultar los resultados",
        ) from error

    return {
        "total": len(resultados),
        "resultados": resultados,
    }