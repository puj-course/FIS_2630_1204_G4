from fastapi import APIRouter, BackgroundTasks, HTTPException, Response, status

from app.services.fachada_recuperacion_contrasena import (
    FachadaRecuperacionContrasena,
    RecuperacionNoDisponibleError,
)
from src.schemas.recuperacion import RespuestaRecuperacion, SolicitudRecuperacion

router = APIRouter()
fachada = FachadaRecuperacionContrasena()

# La respuesta no revela si el correo pertenece a una cuenta.
MENSAJE_RECUPERACION = (
    "Solicitud recibida. Si el correo está registrado, "
    "recibirás instrucciones para recuperar tu contraseña."
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
    # Comprueba que el envio de correos esté configurado antes de aceptar
    # la solicitud. La ruta convierte el error de la fachada en HTTP 503.
    try:
        configuracion = fachada.verificar_disponibilidad()
    except RecuperacionNoDisponibleError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La recuperación de contraseña no está disponible temporalmente",
            headers={"Cache-Control": "no-store"}
        ) from error

    # Programa la creación de la solicitud y el envio del enlace
    # para despues de responder al cliente
    tareas.add_task(
        fachada.procesar_solicitud,
        str(datos.correo),
        configuracion
    )

    # Evita que la respuesta de recuperacion quede almacenada en cache
    respuesta.headers["Cache-Control"] = "no-store"
    return RespuestaRecuperacion(mensaje=MENSAJE_RECUPERACION)