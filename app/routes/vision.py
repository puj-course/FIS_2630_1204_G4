from fastapi import APIRouter, HTTPException, status

from app.services.vision_service import procesar_imagen_base64
from src.schemas.vision import VisionEntrada, VisionRespuesta

router = APIRouter(
    prefix="/vision",
    tags=["Visión"],
)


@router.post(
    "/reconocer",
    response_model=VisionRespuesta,
    summary="Reconocer una letra en una imagen",
    responses={
        400: {
            "description": "Base64 inválido o imagen no admitida",
        },
        500: {
            "description": "Error interno del reconocimiento visual",
        },
    },
)
def reconocer_imagen(datos: VisionEntrada):
    """
    Recibe una imagen JPEG o PNG codificada en Base64.

    - Enviar únicamente el Base64, sin el prefijo data:image.
    - El archivo de imagen no puede superar 5 MiB.
    - El texto Base64 admite hasta 7.000.000 de caracteres.
    - Devuelve la letra reconocida y un mensaje opcional.
    - Si no hay mano o no se reconoce una letra, devuelve letra null.
    """

    try:
        return procesar_imagen_base64(
            imagen_base64=datos.imagen_base64,
            id_secuencia=(
                str(datos.id_secuencia)
                if datos.id_secuencia is not None
                else None
            ),
            modo=datos.modo,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible procesar el reconocimiento visual",
        ) from error