import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.security import obtener_usuario_actual


class TestRutaSesiones(unittest.TestCase):

    def setUp(self):
        self.cliente = TestClient(app)

        self.usuario = {
            "id_usuario": 10,
            "nombre": "Usuario prueba",
            "correo": "prueba@signia.com",
            "rol": "usuario",
        }

        self.sesion = {
            "id_sesion": 100,
            "id_usuario": 10,
            "fecha_inicio": datetime.now(timezone.utc),
            "fecha_fin": None,
            "estado": "activa",
        }

        self.addCleanup(
            lambda: app.dependency_overrides.clear()
        )

    def autenticar_usuario(self):
        app.dependency_overrides[
            obtener_usuario_actual
        ] = lambda: self.usuario

    @patch("app.routes.sesiones.crear_sesion")
    def test_usuario_autenticado_puede_iniciar_sesion(
        self,
        servicio,
    ):
        self.autenticar_usuario()

        servicio.return_value = self.sesion

        respuesta = self.cliente.post(
            "/sesiones",
        )

        self.assertEqual(
            respuesta.status_code,
            201,
        )

        datos = respuesta.json()

        self.assertEqual(
            datos["mensaje"],
            "Sesión de reconocimiento iniciada correctamente",
        )

        self.assertEqual(
            datos["sesion"]["id_usuario"],
            10,
        )

        self.assertEqual(
            datos["sesion"]["estado"],
            "activa",
        )

        servicio.assert_called_once_with(
            id_usuario=10,
        )

    def test_usuario_no_autenticado_no_puede_crear_sesion(
        self,
    ):
        respuesta = self.cliente.post(
            "/sesiones",
        )

        self.assertEqual(
            respuesta.status_code,
            401,
        )

    @patch("app.routes.sesiones.crear_sesion")
    def test_error_del_servicio_devuelve_500(
        self,
        servicio,
    ):
        self.autenticar_usuario()

        servicio.side_effect = Exception(
            "Error de base de datos"
        )

        respuesta = self.cliente.post(
            "/sesiones",
        )

        self.assertEqual(
            respuesta.status_code,
            500,
        )

        self.assertEqual(
            respuesta.json()["detail"],
            "No fue posible iniciar la sesión de reconocimiento",
        )

    @patch("app.routes.sesiones.crear_sesion")
    def test_usuario_no_se_recibe_desde_el_body(
        self,
        servicio,
    ):
        self.autenticar_usuario()

        servicio.return_value = self.sesion

        respuesta = self.cliente.post(
            "/sesiones",
            json={
                "id_usuario": 999,
            },
        )

        self.assertEqual(
            respuesta.status_code,
            201,
        )

        servicio.assert_called_once_with(
            id_usuario=10,
        )


if __name__ == "__main__":
    unittest.main()