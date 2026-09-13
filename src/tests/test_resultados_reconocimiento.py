import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.security import obtener_usuario_actual
from app.services.resultados_reconocimiento_service import (
    LetraDetectadaNoEncontradaError,
    LetraObjetivoNoEncontradaError,
)


class TestRutaResultadosReconocimiento(unittest.TestCase):

    def setUp(self):
        app.dependency_overrides.clear()

        self.cliente = TestClient(app)

        self.usuario = {
            "id_usuario": 9,
            "nombre": "Usuario de prueba",
            "correo": "usuario@signia.local",
            "rol": "usuario",
        }

        self.datos_validos = {
            "id_letra_objetivo": 1,
            "letra_detectada": "A",
            "confianza": 0.95,
        }

    def tearDown(self):
        app.dependency_overrides.clear()

    def autenticar_usuario(self):
        app.dependency_overrides[
            obtener_usuario_actual
        ] = lambda: self.usuario

    def crear_resultado_simulado(self):
        return {
            "id_resultado": 48,
            "id_sesion": 31,
            "id_usuario": 9,
            "id_letra_objetivo": 1,
            "letra_objetivo": "A",
            "id_letra_detectada": 1,
            "letra_detectada": "A",
            "confianza": 0.95,
            "es_correcto": True,
            "fecha_resultado": datetime(
                2026,
                9,
                13,
                tzinfo=timezone.utc,
            ),
        }

    @patch(
        "app.routes.resultados_reconocimiento."
        "registrar_resultado_reconocimiento"
    )
    def test_rechaza_peticion_sin_token(
        self,
        servicio_simulado,
    ):
        respuesta = self.cliente.post(
            "/resultados-reconocimiento",
            json=self.datos_validos,
        )

        self.assertEqual(respuesta.status_code, 401)
        servicio_simulado.assert_not_called()

    @patch(
        "app.routes.resultados_reconocimiento."
        "registrar_resultado_reconocimiento"
    )
    def test_registra_resultado_para_usuario_autenticado(
        self,
        servicio_simulado,
    ):
        self.autenticar_usuario()

        servicio_simulado.return_value = (
            self.crear_resultado_simulado()
        )

        respuesta = self.cliente.post(
            "/resultados-reconocimiento?id_usuario=999",
            json={
                "id_letra_objetivo": 1,
                "letra_detectada": " a ",
                "confianza": 0.95,
            },
        )

        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(
            respuesta.json()["mensaje"],
            "Resultado registrado correctamente",
        )
        self.assertEqual(
            respuesta.json()["resultado"]["id_usuario"],
            9,
        )
        self.assertTrue(
            respuesta.json()["resultado"]["es_correcto"]
        )

        servicio_simulado.assert_called_once_with(
            id_usuario=9,
            id_letra_objetivo=1,
            letra_detectada="A",
            confianza=0.95,
        )

    @patch(
        "app.routes.resultados_reconocimiento."
        "registrar_resultado_reconocimiento"
    )
    def test_rechaza_confianza_fuera_del_rango(
        self,
        servicio_simulado,
    ):
        self.autenticar_usuario()

        respuesta = self.cliente.post(
            "/resultados-reconocimiento",
            json={
                "id_letra_objetivo": 1,
                "letra_detectada": "A",
                "confianza": 2,
            },
        )

        self.assertEqual(respuesta.status_code, 422)
        servicio_simulado.assert_not_called()

    @patch(
        "app.routes.resultados_reconocimiento."
        "registrar_resultado_reconocimiento"
    )
    def test_responde_404_si_objetivo_no_existe(
        self,
        servicio_simulado,
    ):
        self.autenticar_usuario()

        servicio_simulado.side_effect = (
            LetraObjetivoNoEncontradaError(
                "La letra objetivo no existe o no está activa"
            )
        )

        respuesta = self.cliente.post(
            "/resultados-reconocimiento",
            json=self.datos_validos,
        )

        self.assertEqual(respuesta.status_code, 404)
        self.assertEqual(
            respuesta.json(),
            {
                "detail": (
                    "La letra objetivo no existe o no está activa"
                )
            },
        )

    @patch(
        "app.routes.resultados_reconocimiento."
        "registrar_resultado_reconocimiento"
    )
    def test_responde_404_si_detectada_no_existe(
        self,
        servicio_simulado,
    ):
        self.autenticar_usuario()

        servicio_simulado.side_effect = (
            LetraDetectadaNoEncontradaError(
                "La letra detectada no existe o no está activa"
            )
        )

        respuesta = self.cliente.post(
            "/resultados-reconocimiento",
            json=self.datos_validos,
        )

        self.assertEqual(respuesta.status_code, 404)
        self.assertEqual(
            respuesta.json(),
            {
                "detail": (
                    "La letra detectada no existe o no está activa"
                )
            },
        )

    @patch(
        "app.routes.resultados_reconocimiento."
        "registrar_resultado_reconocimiento"
    )
    def test_controla_error_de_base_de_datos(
        self,
        servicio_simulado,
    ):
        self.autenticar_usuario()

        servicio_simulado.side_effect = Exception(
            "Error simulado de conexión"
        )

        respuesta = self.cliente.post(
            "/resultados-reconocimiento",
            json=self.datos_validos,
        )

        self.assertEqual(respuesta.status_code, 500)
        self.assertEqual(
            respuesta.json(),
            {
                "detail": (
                    "No fue posible registrar el resultado"
                )
            },
        )


if __name__ == "__main__":
    unittest.main()