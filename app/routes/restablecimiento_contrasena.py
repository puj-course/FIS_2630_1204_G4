import logging

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute

from app.services.restablecimiento_service import (
    SolicitudRecuperacionInvalidaError,
    restablecer_contrasena
)
from src.schemas.restablecimiento import (
    RespuestaRestablecimiento,
    SolicitudRestablecimiento
)


logger = logging.getLogger(__name__)
NO_CACHE = {"Cache-Control": "no-store"}


class RutaRestablecimiento(APIRoute):
    """Evita incluir contraseñas o tokens en errores de validación de FastAPI."""

    def get_route_handler(self):
        manejador = super().get_route_handler()

        async def manejar_solicitud(solicitud: Request):
            try:
                return await manejador(solicitud)
            except RequestValidationError as error:
                mensaje = "Revisa los campos de la solicitud de restablecimiento."
                errores = error.errors()
                if any(e["loc"] == ("body", "token") for e in errores):
                    mensaje = "El token de recuperación no tiene un formato válido."
                elif any(
                    e["loc"] in (
                        ("body", "nueva_contrasena"),
                        ("body", "confirmacion_contrasena")
                    ) for e in errores
                ):
                    mensaje = "La contraseña y su confirmación deben tener entre 12 y 200 caracteres."
                elif any(
                    e["loc"] == ("body",) and e["type"] == "value_error"
                    for e in errores
                ):
                    mensaje = "Las contraseñas no coinciden."
                raise HTTPException(
                    status_code=422, detail=mensaje, headers=NO_CACHE
                ) from None

        return manejar_solicitud


router = APIRouter(route_class=RutaRestablecimiento)


@router.post(
    "/restablecer-contrasena",
    response_model=RespuestaRestablecimiento
)
def confirmar_restablecimiento(datos: SolicitudRestablecimiento, respuesta: Response):
    try:
        restablecer_contrasena(
            datos.token.get_secret_value(),
            datos.nueva_contrasena.get_secret_value()
        )
    except SolicitudRecuperacionInvalidaError:
        raise HTTPException(
            status_code=400,
            detail="El enlace de recuperación no es válido o ha vencido. Solicita uno nuevo.",
            headers=NO_CACHE
        ) from None
    except Exception as error:
        logger.error(
            "No fue posible restablecer una contraseña (%s)",
            type(error).__name__
        )
        raise HTTPException(
            status_code=500,
            detail="No fue posible actualizar la contraseña. Inténtalo nuevamente.",
            headers=NO_CACHE
        ) from None

    respuesta.headers.update(NO_CACHE)
    return RespuestaRestablecimiento(
        mensaje="Contraseña actualizada correctamente. Ya puedes iniciar sesión."
    )
