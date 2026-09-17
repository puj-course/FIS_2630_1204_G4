import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.security import obtener_usuario_actual


class TestConsultaProgreso(unittest.TestCase):

    def setUp(self):
        dependencias = patch.dict(
            app.dependency_overrides,
            {},
            clear=True,
        )
        dependencias.start()
        self.addCleanup(dependencias.stop)

        self.cliente = TestClient(app)
        self.addCleanup(self.cliente.close)

        consulta = patch(
            "app.routes.progreso.consultar_progreso_usuario"
        )
        self.consultar = consulta.start()
        self.addCleanup(consulta.stop)

    def autenticar_usuario(self, id_usuario=9):
        usuario = {
            "id_usuario": id_usuario,
            "nombre": "Usuario de prueba",
            "correo": f"usuario{id_usuario}@signia.local",
            "rol": "usuario",
        }

        app.dependency_overrides[
            obtener_usuario_actual
        ] = lambda: usuario

    def crear_progresos(self, id_usuario):
        fecha = datetime(2026, 9, 17, tzinfo=timezone.utc)

        return [
            {
                "id_progreso": 10,
                "id_usuario": id_usuario,
                "id_letra": 1,
                "letra": "A",
                "cantidad_intentos": 5,
                "cantidad_aciertos": 4,
                "dominada": True,
                "fecha_ultima_practica": fecha,
                "fecha_actualizacion": fecha,
            },
            {
                "id_progreso": 11,
                "id_usuario": id_usuario,
                "id_letra": 2,
                "letra": "B",
                "cantidad_intentos": 0,
                "cantidad_aciertos": 0,
                "dominada": False,
                "fecha_ultima_practica": None,
                "fecha_actualizacion": fecha,
            },
        ]

    def test_consulta_para_el_usuario_autenticado(self):
        for id_usuario in (9, 15):
            with self.subTest(id_usuario=id_usuario):
                self.consultar.reset_mock()
                self.autenticar_usuario(id_usuario)

                self.consultar.return_value = (
                    self.crear_progresos(id_usuario)
                )

                respuesta = self.cliente.get(
                    "/progreso?id_usuario=999"
                )

                self.assertEqual(respuesta.status_code, 200)

                cuerpo = respuesta.json()
                progresos = cuerpo["progresos"]

                self.assertEqual(cuerpo["total"], 2)
                self.assertEqual(len(progresos), 2)

                self.assertEqual(
                    [p["id_usuario"] for p in progresos],
                    [id_usuario, id_usuario],
                )
                self.assertEqual(
                    [p["id_letra"] for p in progresos],
                    [1, 2],
                )
                self.assertEqual(
                    [p["letra"] for p in progresos],
                    ["A", "B"],
                )
                self.assertEqual(
                    [p["dominada"] for p in progresos],
                    [True, False],
                )
                self.assertEqual(
                    progresos[0]["cantidad_intentos"],
                    5,
                )
                self.assertEqual(
                    progresos[0]["cantidad_aciertos"],
                    4,
                )
                self.assertIsNone(
                    progresos[1]["fecha_ultima_practica"]
                )

                self.consultar.assert_called_once_with(
                    id_usuario=id_usuario,
                )

    def test_usuario_sin_progreso_recibe_lista_vacia(self):
        self.autenticar_usuario()
        self.consultar.return_value = []

        respuesta = self.cliente.get("/progreso")

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            respuesta.json(),
            {
                "total": 0,
                "progresos": [],
            },
        )
        self.consultar.assert_called_once_with(
            id_usuario=9,
        )

    def test_rechaza_consulta_sin_autenticacion(self):
        respuesta = self.cliente.get("/progreso")

        self.assertEqual(respuesta.status_code, 401)
        self.assertEqual(
            respuesta.headers.get("www-authenticate"),
            "Bearer",
        )
        self.consultar.assert_not_called()

    def test_controla_error_del_servicio(self):
        self.autenticar_usuario()

        self.consultar.side_effect = RuntimeError(
            "Detalle interno de la base de datos"
        )

        with self.assertLogs(
            "app.routes.progreso",
            level="ERROR",
        ):
            respuesta = self.cliente.get("/progreso")

        self.assertEqual(respuesta.status_code, 500)
        self.assertEqual(
            respuesta.json(),
            {
                "detail": "No fue posible consultar el progreso",
            },
        )
        self.assertNotIn(
            "Detalle interno",
            respuesta.text,
        )
        self.consultar.assert_called_once_with(
            id_usuario=9,
        )


if __name__ == "__main__":
    unittest.main()