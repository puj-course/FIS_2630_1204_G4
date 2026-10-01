import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routes.intentos import router
from app.security import obtener_usuario_actual


class TestConsultaIntentosRuta(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.app.include_router(router)

        self.app.dependency_overrides[obtener_usuario_actual] = (
            lambda: {"id_usuario": 9}
        )

        self.cliente = TestClient(self.app)
        self.addCleanup(self.cliente.close)

        parche = patch(
            "app.routes.intentos.consultar_intentos_usuario"
        )
        self.consultar = parche.start()
        self.addCleanup(parche.stop)

        self.intento = {
            "id_intento": 1,
            "id_resultado": 20,
            "id_usuario": 9,
            "id_sesion": 10,
            "id_letra": 2,
            "es_correcto": True,
            "fecha_intento": "2026-09-30T12:00:00Z",
        }

        self.consultar.return_value = [self.intento]

    def test_devuelve_intentos_del_usuario_autenticado(self):
        respuesta = self.cliente.get("/intentos")

        self.assertEqual(
            respuesta.status_code,
            200,
            respuesta.text,
        )
        self.assertEqual(
            respuesta.json(),
            {
                "total": 1,
                "intentos": [self.intento],
            },
        )
        self.consultar.assert_called_once_with(
            id_usuario=9,
            id_letra=None,
            id_sesion=None,
        )

    def test_envia_los_filtros_al_servicio(self):
        casos = [
            ({}, None, None),
            ({"id_letra": 2}, 2, None),
            ({"id_sesion": 10}, None, 10),
            (
                {"id_letra": 2, "id_sesion": 10},
                2,
                10,
            ),
        ]

        for parametros, letra, sesion in casos:
            with self.subTest(parametros=parametros):
                self.consultar.reset_mock()

                respuesta = self.cliente.get(
                    "/intentos",
                    params=parametros,
                )

                self.assertEqual(
                    respuesta.status_code,
                    200,
                    respuesta.text,
                )
                self.consultar.assert_called_once_with(
                    id_usuario=9,
                    id_letra=letra,
                    id_sesion=sesion,
                )

    def test_devuelve_lista_vacia_sin_coincidencias(self):
        self.consultar.return_value = []

        respuesta = self.cliente.get("/intentos")

        self.assertEqual(
            respuesta.status_code,
            200,
            respuesta.text,
        )
        self.assertEqual(
            respuesta.json(),
            {
                "total": 0,
                "intentos": [],
            },
        )

    def test_no_permite_cambiar_usuario_desde_la_url(self):
        respuesta = self.cliente.get(
            "/intentos",
            params={
                "id_usuario": 999,
                "id_sesion": 10,
            },
        )

        self.assertEqual(
            respuesta.status_code,
            200,
            respuesta.text,
        )
        self.consultar.assert_called_once_with(
            id_usuario=9,
            id_letra=None,
            id_sesion=10,
        )

    def test_rechaza_consulta_sin_autenticacion(self):
        self.app.dependency_overrides.clear()

        respuesta = self.cliente.get("/intentos")

        self.assertEqual(
            respuesta.status_code,
            401,
            respuesta.text,
        )
        self.assertEqual(
            respuesta.headers.get("www-authenticate"),
            "Bearer",
        )
        self.consultar.assert_not_called()

    def test_rechaza_token_invalido(self):
        self.app.dependency_overrides.clear()

        with patch(
            "app.security.obtener_clave_jwt",
            return_value="clave-exclusiva-para-pruebas-de-intentos-373",
        ):
            respuesta = self.cliente.get(
                "/intentos",
                headers={
                    "Authorization": "Bearer token-invalido",
                },
            )

        self.assertEqual(
            respuesta.status_code,
            401,
            respuesta.text,
        )
        self.consultar.assert_not_called()

    def test_rechaza_filtros_invalidos(self):
        for campo in ("id_letra", "id_sesion"):
            for valor in ("0", "-1", "abc", "1.5", ""):
                with self.subTest(campo=campo, valor=valor):
                    self.consultar.reset_mock()

                    respuesta = self.cliente.get(
                        "/intentos",
                        params={campo: valor},
                    )

                    self.assertEqual(
                        respuesta.status_code,
                        422,
                        respuesta.text,
                    )
                    self.consultar.assert_not_called()

    def test_oculta_detalles_de_errores_internos(self):
        self.consultar.side_effect = RuntimeError(
            "Detalle interno de la conexión"
        )

        respuesta = self.cliente.get("/intentos")

        self.assertEqual(
            respuesta.status_code,
            500,
            respuesta.text,
        )
        self.assertEqual(
            respuesta.json(),
            {
                "detail": "No fue posible consultar los intentos",
            },
        )


if __name__ == "__main__":
    unittest.main()