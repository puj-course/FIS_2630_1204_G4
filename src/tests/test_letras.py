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
    @patch("app.routes.letras.obtener_letra_por_id")
    def test_devuelve_una_letra_por_id(self, servicio_simulado):
        letra = {
            "id_letra": 1,
            "letra": "A",
            "descripcion": "Letra A",
            "ruta_imagen": "assets/alfabeto/a.png"
        }

        servicio_simulado.return_value = letra

        respuesta = self.cliente.get("/letras/1")

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json(), letra)
        servicio_simulado.assert_called_once_with(1)

    @patch("app.routes.letras.obtener_letra_por_id")
    def test_responde_404_si_la_letra_no_existe(
        self,
        servicio_simulado
    ):
        servicio_simulado.return_value = None

        respuesta = self.cliente.get("/letras/999999")

        self.assertEqual(respuesta.status_code, 404)
        self.assertEqual(
            respuesta.json(),
            {"detail": "La letra solicitada no existe"}
        )

    @patch("app.routes.letras.obtener_letra_por_id")
    def test_controla_error_al_consultar_una_letra(
        self,
        servicio_simulado
    ):
        servicio_simulado.side_effect = Exception(
            "Error simulado de conexión"
        )

        respuesta = self.cliente.get("/letras/1")

        self.assertEqual(respuesta.status_code, 500)
        self.assertEqual(
            respuesta.json(),
            {"detail": "No fue posible consultar la letra"}
        )

if __name__ == "__main__":
    unittest.main()