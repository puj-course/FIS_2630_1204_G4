import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


class TestConsultaLetras(unittest.TestCase):

    def setUp(self):
        self.cliente = TestClient(app)

    @patch("app.routes.letras.obtener_letras_registradas")
    def test_devuelve_las_letras_registradas(self, servicio_simulado):
        datos = [
            {
                "id_letra": 1,
                "letra": "A",
                "descripcion": "Letra A",
                "ruta_imagen": "assets/alfabeto/a.png"
            }
        ]

        servicio_simulado.return_value = datos

        respuesta = self.cliente.get(
            "/letras",
            headers={"Origin": "http://localhost:5173"}
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json(), datos)
        self.assertEqual(
            respuesta.headers["access-control-allow-origin"],
            "http://localhost:5173"
        )

    @patch("app.routes.letras.obtener_letras_registradas")
    def test_devuelve_lista_vacia(self, servicio_simulado):
        servicio_simulado.return_value = []

        respuesta = self.cliente.get("/letras")

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json(), [])

    @patch("app.routes.letras.obtener_letras_registradas")
    def test_controla_error_de_base_de_datos(self, servicio_simulado):
        servicio_simulado.side_effect = Exception(
            "Error simulado de conexión"
        )

        respuesta = self.cliente.get("/letras")

        self.assertEqual(respuesta.status_code, 500)
        self.assertEqual(
            respuesta.json(),
            {"detail": "No fue posible consultar las letras"}
        )


if __name__ == "__main__":
    unittest.main()