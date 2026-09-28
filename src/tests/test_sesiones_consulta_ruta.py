import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.security import obtener_usuario_actual


class TestRutaConsultaSesiones(unittest.TestCase):

    def setUp(self):
        self.cliente = TestClient(app)

        self.usuario = {
            "id_usuario": 10,
            "nombre": "Usuario prueba",
            "correo": "prueba@signia.com",
            "rol": "usuario",
        }

        self.sesiones = [
            {
                "id_sesion": 100,
                "id_usuario": 10,
                "fecha_inicio": datetime.now(timezone.utc),
                "fecha_fin": None,
                "estado": "activa",
            },
            {
                "id_sesion": 99,
                "id_usuario": 10,
                "fecha_inicio": datetime.now(timezone.utc),
                "fecha_fin": datetime.now(timezone.utc),
                "estado": "finalizada",
            },
        ]

        self.addCleanup(
            lambda: app.dependency_overrides.clear()
        )

    def autenticar_usuario(self):
        app.dependency_overrides[
            obtener_usuario_actual
        ] = lambda: self.usuario


    @patch("app.routes.sesiones.consultar_sesiones_usuario")
    def test_usuario_puede_consultar_sus_sesiones(
        self,
        servicio,
    ):
        self.autenticar_usuario()

        servicio.return_value = self.sesiones

        respuesta = self.cliente.get(
            "/sesiones",
        )

        self.assertEqual(
            respuesta.status_code,
            200,
        )

        datos = respuesta.json()

        self.assertEqual(
            datos["total"],
            2,
        )

        self.assertEqual(
            datos["sesiones"][0]["id_usuario"],
            10,
        )

        servicio.assert_called_once_with(
            id_usuario=10,
        )


    @patch("app.routes.sesiones.consultar_sesiones_usuario")
    def test_usuario_sin_sesiones_recibe_lista_vacia(
        self,
        servicio,
    ):
        self.autenticar_usuario()

        servicio.return_value = []

        respuesta = self.cliente.get(
            "/sesiones",
        )

        self.assertEqual(
            respuesta.status_code,
            200,
        )

        datos = respuesta.json()

        self.assertEqual(
            datos["total"],
            0,
        )

        self.assertEqual(
            datos["sesiones"],
            [],
        )


    def test_usuario_no_autenticado_no_consulta_sesiones(
        self,
    ):
        respuesta = self.cliente.get(
            "/sesiones",
        )

        self.assertEqual(
            respuesta.status_code,
            401,
        )


    @patch("app.routes.sesiones.consultar_sesiones_usuario")
    def test_error_del_servicio_devuelve_500(
        self,
        servicio,
    ):
        self.autenticar_usuario()

        servicio.side_effect = Exception(
            "Error de base de datos"
        )

        respuesta = self.cliente.get(
            "/sesiones",
        )

        self.assertEqual(
            respuesta.status_code,
            500,
        )

        self.assertEqual(
            respuesta.json()["detail"],
            "No fue posible consultar las sesiones",
        )


if __name__ == "__main__":
    unittest.main()