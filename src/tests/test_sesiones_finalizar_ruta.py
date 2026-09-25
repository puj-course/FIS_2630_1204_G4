import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.security import obtener_usuario_actual
from app.services.sesiones_service import (
    EstadoSesionError,
    SesionNoEncontradaError,
)


class TestRutaFinalizarSesiones(unittest.TestCase):

    def setUp(self):
        self.cliente = TestClient(app)

        self.usuario = {
            "id_usuario": 10,
            "nombre": "Usuario prueba",
            "correo": "prueba@signia.com",
            "rol": "usuario",
        }

        self.sesion_finalizada = {
            "id_sesion": 100,
            "id_usuario": 10,
            "fecha_inicio": datetime.now(timezone.utc),
            "fecha_fin": datetime.now(timezone.utc),
            "estado": "finalizada",
        }

        self.addCleanup(
            lambda: app.dependency_overrides.clear()
        )

    def autenticar_usuario(self):
        app.dependency_overrides[
            obtener_usuario_actual
        ] = lambda: self.usuario


    @patch("app.routes.sesiones.finalizar_sesion")
    def test_usuario_puede_finalizar_sesion_propia(
        self,
        servicio,
    ):
        self.autenticar_usuario()

        servicio.return_value = self.sesion_finalizada

        respuesta = self.cliente.patch(
            "/sesiones/100/finalizar",
        )

        self.assertEqual(
            respuesta.status_code,
            200,
        )

        datos = respuesta.json()

        self.assertEqual(
            datos["mensaje"],
            "Sesión finalizada correctamente",
        )

        self.assertEqual(
            datos["sesion"]["estado"],
            "finalizada",
        )

        servicio.assert_called_once_with(
            id_usuario=10,
            id_sesion=100,
        )


    def test_usuario_no_autenticado_no_puede_finalizar_sesion(
        self,
    ):
        respuesta = self.cliente.patch(
            "/sesiones/100/finalizar",
        )

        self.assertEqual(
            respuesta.status_code,
            401,
        )


    @patch("app.routes.sesiones.finalizar_sesion")
    def test_sesion_inexistente_devuelve_404(
        self,
        servicio,
    ):
        self.autenticar_usuario()

        servicio.side_effect = SesionNoEncontradaError(
            "No se encontró la sesión para este usuario"
        )

        respuesta = self.cliente.patch(
            "/sesiones/100/finalizar",
        )

        self.assertEqual(
            respuesta.status_code,
            404,
        )


    @patch("app.routes.sesiones.finalizar_sesion")
    def test_sesion_no_finalizable_devuelve_409(
        self,
        servicio,
    ):
        self.autenticar_usuario()

        servicio.side_effect = EstadoSesionError(
            "Solo se pueden finalizar sesiones activas"
        )

        respuesta = self.cliente.patch(
            "/sesiones/100/finalizar",
        )

        self.assertEqual(
            respuesta.status_code,
            409,
        )


    @patch("app.routes.sesiones.finalizar_sesion")
    def test_error_del_servicio_devuelve_500(
        self,
        servicio,
    ):
        self.autenticar_usuario()

        servicio.side_effect = Exception(
            "Error de base de datos"
        )

        respuesta = self.cliente.patch(
            "/sesiones/100/finalizar",
        )

        self.assertEqual(
            respuesta.status_code,
            500,
        )

        self.assertEqual(
            respuesta.json()["detail"],
            "No fue posible finalizar la sesión",
        )


if __name__ == "__main__":
    unittest.main()