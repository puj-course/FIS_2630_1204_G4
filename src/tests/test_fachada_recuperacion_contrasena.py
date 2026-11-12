import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from app.services import restablecimiento_service
from app.services.correo_recuperacion_service import ConfiguracionCorreo, ConfiguracionCorreoError
from app.services.fachada_recuperacion_contrasena import (
    FachadaRecuperacionContrasena,
    RecuperacionNoDisponibleError,
    SolicitudRecuperacionInvalidaError,
)
from app.services.recuperacion_service import RecuperacionCreada

MODULO = "app.services.fachada_recuperacion_contrasena"


class TestFachadaRecuperacionContrasena(unittest.TestCase):
    def setUp(self):
        self.fachada = FachadaRecuperacionContrasena()
        self.configuracion = ConfiguracionCorreo(
            host="smtp-mail.outlook.com",
            puerto=587,
            seguridad="starttls",
            usuario="cuenta@example.com",
            client_id="11111111-2222-4333-8444-555555555555",
            remitente="cuenta@example.com",
            url_recuperacion="https://signia.example.com/restablecer-contrasena"
        )
        self.solicitud = RecuperacionCreada(
            id_recuperacion=20,
            correo="persona@example.com",
            token="token-exclusivo-de-prueba",
            fecha_expiracion=datetime(2026, 1, 1, 12, 15, tzinfo=timezone.utc)
        )

        for atributo, funcion in (
            ("configurar", "obtener_configuracion_correo"),
            ("crear", "crear_solicitud_recuperacion"),
            ("enviar", "enviar_correo_recuperacion"),
            ("restablecer", "restablecer_contrasena")
        ):
            parche = patch(f"{MODULO}.{funcion}")
            setattr(self, atributo, parche.start())
            self.addCleanup(parche.stop)

    def test_verificar_disponibilidad_devuelve_la_configuracion(self):
        self.configurar.return_value = self.configuracion

        self.assertIs(self.fachada.verificar_disponibilidad(), self.configuracion)

    def test_verificar_disponibilidad_oculta_el_error_de_configuracion(self):
        error = ConfiguracionCorreoError("Error simulado")
        self.configurar.side_effect = error

        with self.assertRaises(RecuperacionNoDisponibleError) as contexto:
            self.fachada.verificar_disponibilidad()

        self.assertIs(contexto.exception.__cause__, error)
        self.assertNotIn("Error simulado", str(contexto.exception))

    def test_procesar_solicitud_crea_la_solicitud_y_envia_el_correo(self):
        self.crear.return_value = self.solicitud

        self.fachada.procesar_solicitud("persona@example.com", self.configuracion)

        self.crear.assert_called_once_with("persona@example.com")
        self.enviar.assert_called_once_with(
            correo=self.solicitud.correo,
            token=self.solicitud.token,
            fecha_expiracion=self.solicitud.fecha_expiracion,
            configuracion=self.configuracion
        )

    def test_procesar_solicitud_no_envia_correo_si_no_hay_solicitud(self):
        self.crear.return_value = None

        self.fachada.procesar_solicitud("nadie@example.com", self.configuracion)

        self.crear.assert_called_once_with("nadie@example.com")
        self.enviar.assert_not_called()

    def test_procesar_solicitud_registra_errores_sin_exponer_datos(self):
        secreto = f"{self.solicitud.correo} {self.solicitud.token}"

        for funcion in ("crear", "enviar"):
            with self.subTest(funcion=funcion):
                self.crear.side_effect = None
                self.crear.return_value = self.solicitud
                self.enviar.side_effect = None
                getattr(self, funcion).side_effect = RuntimeError(secreto)

                with self.assertLogs(MODULO, level="ERROR") as logs:
                    self.fachada.procesar_solicitud(
                        "persona@example.com", self.configuracion
                    )

                salida = " ".join(logs.output)
                self.assertIn("RuntimeError", salida)
                self.assertNotIn(self.solicitud.correo, salida)
                self.assertNotIn(self.solicitud.token, salida)

    def test_restablecer_contrasena_delega_en_el_servicio(self):
        self.fachada.restablecer_contrasena("token-de-prueba", "Clave nueva 2077!")

        self.restablecer.assert_called_once_with("token-de-prueba", "Clave nueva 2077!")

    def test_restablecer_contrasena_propaga_el_token_invalido(self):
        self.restablecer.side_effect = SolicitudRecuperacionInvalidaError()

        with self.assertRaises(SolicitudRecuperacionInvalidaError):
            self.fachada.restablecer_contrasena("token-de-prueba", "Clave nueva 2077!")

    def test_reexporta_la_excepcion_del_servicio(self):
        self.assertIs(
            SolicitudRecuperacionInvalidaError,
            restablecimiento_service.SolicitudRecuperacionInvalidaError
        )


if __name__ == "__main__":
    unittest.main()