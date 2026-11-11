import logging

from app.services.correo_recuperacion_service import (
    ConfiguracionCorreo,
    ConfiguracionCorreoError,
    enviar_correo_recuperacion,
    obtener_configuracion_correo,
)
from app.services.recuperacion_service import crear_solicitud_recuperacion
from app.services.restablecimiento_service import (
    SolicitudRecuperacionInvalidaError,
    restablecer_contrasena,
)

logger = logging.getLogger(__name__)

# Define lo que otros modulos pueden importar como interfaz publica de la fachada
__all__ = [
    "FachadaRecuperacionContrasena",
    "RecuperacionNoDisponibleError",
    "SolicitudRecuperacionInvalidaError",
]


class RecuperacionNoDisponibleError(Exception):
    """La recuperación no se puede atender porque el correo no está configurado."""


class FachadaRecuperacionContrasena:
    """Punto único de acceso al flujo de recuperación de contraseña.

    Coordina la configuración del correo, la creación de la solicitud,
    el envío del enlace y el cambio de contraseña, para que las rutas
    no dependan de cada servicio por separado.
    """

    def verificar_disponibilidad(self) -> ConfiguracionCorreo:
        """Obtiene la configuración necesaria para enviar el correo.

        Traduce el error del servicio de correo a un error propio
        de la fachada, que la ruta puede manejar.
        """
        try:
            return obtener_configuracion_correo()
        except ConfiguracionCorreoError as error:
            raise RecuperacionNoDisponibleError() from error

    def procesar_solicitud(
        self,
        correo: str,
        configuracion: ConfiguracionCorreo
    ) -> None:
        """Crea la solicitud y envía el enlace cuando se generó una.

        Los errores se registran sin interrumpir la respuesta de la ruta.
        """
        try:
            solicitud = crear_solicitud_recuperacion(correo)

            # Si el servicio no genero una solicitud, no hay enlace que enviar
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

    def restablecer_contrasena(self, token: str, nueva_contrasena: str) -> None:
        """Delega el cambio de contraseña y deja que la ruta maneje sus errores."""
        restablecer_contrasena(token, nueva_contrasena)