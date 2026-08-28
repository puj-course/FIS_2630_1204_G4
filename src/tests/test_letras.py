import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.security import (
    obtener_usuario_actual,
    requerir_administrador
)

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

    @patch(
        "app.routes.letras.actualizar_informacion_letra"
    )
    def test_actualiza_una_letra(
        self,
        servicio_simulado
    ):
        letra_actualizada = {
            "id_letra": 1,
            "letra": "A",
            "descripcion": "Descripción actualizada",
            "ruta_imagen": "assets/alfabeto/a.png"
        }

        servicio_simulado.return_value = letra_actualizada

        respuesta = self.cliente.patch(
            "/letras/1",
            json={
                "descripcion": "Descripción actualizada"
            }
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            respuesta.json(),
            {
                "mensaje": (
                    "La letra fue actualizada correctamente"
                ),
                "letra": letra_actualizada
            }
        )
        servicio_simulado.assert_called_once_with(
            1,
            {"descripcion": "Descripción actualizada"}
        )

    @patch(
        "app.routes.letras.actualizar_informacion_letra"
    )
    def test_rechaza_actualizacion_sin_campos(
        self,
        servicio_simulado
    ):
        respuesta = self.cliente.patch(
            "/letras/1",
            json={}
        )

        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(
            respuesta.json(),
            {
                "detail": (
                    "Debe enviar al menos un campo para actualizar"
                )
            }
        )
        servicio_simulado.assert_not_called()

    @patch(
        "app.routes.letras.actualizar_informacion_letra"
    )
    def test_actualizacion_responde_404_si_no_existe(
        self,
        servicio_simulado
    ):
        servicio_simulado.return_value = None

        respuesta = self.cliente.patch(
            "/letras/999999",
            json={
                "descripcion": "Nueva descripción"
            }
        )

        self.assertEqual(respuesta.status_code, 404)
        self.assertEqual(
            respuesta.json(),
            {"detail": "La letra solicitada no existe"}
        )

    @patch(
        "app.routes.letras.actualizar_informacion_letra"
    )
    def test_controla_error_al_actualizar_letra(
        self,
        servicio_simulado
    ):
        servicio_simulado.side_effect = Exception(
            "Error simulado de conexión"
        )

        respuesta = self.cliente.patch(
            "/letras/1",
            json={
                "descripcion": "Nueva descripción"
            }
        )

        self.assertEqual(respuesta.status_code, 500)
        self.assertEqual(
            respuesta.json(),
            {"detail": "No fue posible actualizar la letra"}
        )
class TestPermisosActualizacionLetra(unittest.TestCase):

    def setUp(self):
        self.cliente = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.pop(
            obtener_usuario_actual,
            None
        )
        app.dependency_overrides.pop(
            requerir_administrador,
            None
        )

    @patch("app.routes.letras.actualizar_informacion_letra")
    def test_rechaza_actualizacion_sin_autenticacion(
        self,
        servicio_simulado
    ):
        respuesta = self.cliente.patch(
            "/letras/1",
            json={"descripcion": "Descripción modificada"}
        )

        self.assertEqual(respuesta.status_code, 401)
        self.assertEqual(
            respuesta.json(),
            {"detail": "No fue posible validar las credenciales"}
        )
        servicio_simulado.assert_not_called()

    @patch("app.routes.letras.actualizar_informacion_letra")
    def test_rechaza_actualizacion_de_usuario_normal(
        self,
        servicio_simulado
    ):
        app.dependency_overrides[obtener_usuario_actual] = lambda: {
            "id_usuario": 1,
            "nombre": "Usuario de prueba",
            "correo": "usuario.prueba@signia.local",
            "rol": "usuario"
        }

        respuesta = self.cliente.patch(
            "/letras/1",
            json={"descripcion": "Descripción modificada"}
        )

        self.assertEqual(respuesta.status_code, 403)
        self.assertEqual(
            respuesta.json(),
            {
                "detail":
                "No tiene permisos para modificar el alfabeto"
            }
        )
        servicio_simulado.assert_not_called()

    @patch("app.routes.letras.actualizar_informacion_letra")
    def test_permite_actualizacion_de_administrador(
        self,
        servicio_simulado
    ):
        app.dependency_overrides[obtener_usuario_actual] = lambda: {
            "id_usuario": 2,
            "nombre": "Administrador de prueba",
            "correo": "admin.prueba@signia.local",
            "rol": "administrador"
        }

        letra_actualizada = {
            "id_letra": 1,
            "letra": "A",
            "descripcion": "Descripción modificada",
            "ruta_imagen": "assets/alfabeto/a.png"
        }
        servicio_simulado.return_value = letra_actualizada

        respuesta = self.cliente.patch(
            "/letras/1",
            json={"descripcion": "Descripción modificada"}
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            respuesta.json(),
            {
                "mensaje": "La letra fue actualizada correctamente",
                "letra": letra_actualizada
            }
        )
        servicio_simulado.assert_called_once_with(
            1,
            {"descripcion": "Descripción modificada"}
        )

if __name__ == "__main__":
    unittest.main()