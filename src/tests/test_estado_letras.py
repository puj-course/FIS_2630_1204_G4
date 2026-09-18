import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.security import obtener_usuario_actual


class TestEstadoLetras(unittest.TestCase):

    def setUp(self):
        reemplazo = patch.dict(
            app.dependency_overrides,
            {},
            clear=True,
        )
        reemplazo.start()
        self.addCleanup(reemplazo.stop)

        self.cliente = TestClient(app)
        self.addCleanup(self.cliente.close)

    def autenticar_usuario(self, id_usuario=9):
        usuario = {
            "id_usuario": id_usuario,
            "nombre": "Usuario de prueba",
            "correo": f"usuario-{id_usuario}@signia.local",
            "rol": "usuario",
        }

        app.dependency_overrides[
            obtener_usuario_actual
        ] = lambda: usuario

    @patch(
        "app.routes.progreso.consultar_estado_letras_usuario"
    )
    def test_consulta_utiliza_usuario_autenticado(
        self,
        servicio_simulado,
    ):
        for id_usuario, estado in (
            (9, "aprendida"),
            (15, "pendiente"),
        ):
            with self.subTest(id_usuario=id_usuario):
                self.autenticar_usuario(id_usuario)
                servicio_simulado.reset_mock()

                letras = [
                    {
                        "id_letra": 1,
                        "letra": "A",
                        "descripcion": "Descripción de A",
                        "ruta_imagen": "/assets/alfabeto/a.png",
                        "estado": estado,
                    },
                    {
                        "id_letra": 2,
                        "letra": "B",
                        "descripcion": None,
                        "ruta_imagen": None,
                        "estado": "pendiente",
                    },
                ]

                servicio_simulado.return_value = letras

                # Intenta indicar otro usuario en la URL.
                respuesta = self.cliente.get(
                    "/progreso/letras?id_usuario=999"
                )

                self.assertEqual(
                    respuesta.status_code,
                    200,
                )
                self.assertEqual(
                    respuesta.json(),
                    {
                        "total": 2,
                        "letras": letras,
                    },
                )

                # La ruta debe utilizar el usuario autenticado.
                servicio_simulado.assert_called_once_with(
                    id_usuario=id_usuario,
                )

    @patch(
        "app.routes.progreso.consultar_estado_letras_usuario"
    )
    def test_sin_letras_devuelve_lista_vacia(
        self,
        servicio_simulado,
    ):
        self.autenticar_usuario()
        servicio_simulado.return_value = []

        respuesta = self.cliente.get("/progreso/letras")

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            respuesta.json(),
            {
                "total": 0,
                "letras": [],
            },
        )
        servicio_simulado.assert_called_once_with(
            id_usuario=9,
        )

    @patch(
        "app.routes.progreso.consultar_estado_letras_usuario"
    )
    def test_rechaza_solicitud_sin_autenticacion(
        self,
        servicio_simulado,
    ):
        respuesta = self.cliente.get("/progreso/letras")

        self.assertEqual(respuesta.status_code, 401)
        servicio_simulado.assert_not_called()

    @patch(
        "app.routes.progreso.consultar_estado_letras_usuario"
    )
    def test_controla_error_del_servicio(
        self,
        servicio_simulado,
    ):
        self.autenticar_usuario()
        servicio_simulado.side_effect = RuntimeError(
            "Error interno simulado"
        )

        with self.assertLogs(
            "app.routes.progreso",
            level="ERROR",
        ):
            respuesta = self.cliente.get("/progreso/letras")

        self.assertEqual(respuesta.status_code, 500)
        self.assertEqual(
            respuesta.json(),
            {
                "detail": (
                    "No fue posible consultar el estado de las letras"
                ),
            },
        )
        servicio_simulado.assert_called_once_with(
            id_usuario=9,
        )


if __name__ == "__main__":
    unittest.main()