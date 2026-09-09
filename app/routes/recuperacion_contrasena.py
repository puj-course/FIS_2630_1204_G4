import logging

from fastapi import (
    APIRouter,
    BackgroundTasks,
    HTTPException,
    Response,
    status
)

from app.services.correo_recuperacion_service import (
    ConfiguracionCorreo,
    ConfiguracionCorreoError,
    enviar_correo_recuperacion,
    obtener_configuracion_correo
)
from app.services.recuperacion_service import crear_solicitud_recuperacion
from src.schemas.recuperacion import RespuestaRecuperacion, SolicitudRecuperacion


logger = logging.getLogger(__name__)
router = APIRouter()

MENSAJE_RECUPERACION = (
    "Solicitud recibida. Si el correo está registrado, "
    "recibirás instrucciones para recuperar tu contraseña."
)


def procesar_solicitud_recuperacion(
    correo: str,
    configuracion: ConfiguracionCorreo
) -> None:
    try:
        solicitud = crear_solicitud_recuperacion(correo)

        if solicitud is not None:
            enviar_correo_recuperacion(
                correo=solicitud.correo,
                token=solicitud.token,
                fecha_expiracion=solicitud.fecha_expiracion,
                configuracion=configuracion
            )
    except Exception as error:
        # Solo se registra el tipo de error para evitar exponer datos del correo
        logger.error(
            "No fue posible procesar una recuperación de contraseña (%s)",
            type(error).__name__
        )


@router.post(
    "/recuperar-contrasena",
    response_model=RespuestaRecuperacion,
    status_code=status.HTTP_202_ACCEPTED
)
def solicitar_recuperacion(
    datos: SolicitudRecuperacion,
    tareas: BackgroundTasks,
    respuesta: Response
):
    try:
        configuracion = obtener_configuracion_correo()
    except ConfiguracionCorreoError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La recuperación de contraseña no está disponible temporalmente",
            headers={"Cache-Control": "no-store"}
        ) from error

    tareas.add_task(
        procesar_solicitud_recuperacion,
        str(datos.correo),
        configuracion
    )
    respuesta.headers["Cache-Control"] = "no-store"
    return RespuestaRecuperacion(mensaje=MENSAJE_RECUPERACION)
