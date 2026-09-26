import unittest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.security import obtener_usuario_actual
from app.services.resultados_service import (
    SesionNoEncontradaError,
    UsuarioSesionError,
)


class TestConsultaResultadosSesion(unittest.TestCase):
    def setUp(self):
        anteriores = app.dependency_overrides.copy()
        app.dependency_overrides.clear()
        self.addCleanup(self.restaurar_overrides, anteriores)

        self.cliente = TestClient(app)
        self.addCleanup(self.cliente.close)

        parche = patch(
            "app.routes.resultados.consultar_resultados_sesion"
        )
        self.servicio = parche.start()
        self.addCleanup(parche.stop)

        self.usuario = {
            "id_usuario": 9,
            "nombre": "Usuario de prueba",
            "correo": "consulta@signia.local",
            "rol": "usuario",
        }

    def restaurar_overrides(self, anteriores):
        app.dependency_overrides.clear()
        app.dependency_overrides.update(anteriores)

    def autenticar(self):
        app.dependency_overrides[obtener_usuario_actual] = (
            lambda: self.usuario
        )

    def test_consulta_con_usuario_del_token(self):
        self.autenticar()

        fecha = datetime(2026, 9, 26, tzinfo=timezone.utc)

        self.servicio.return_value = [
            {
                "id_resultado": 41,
                "id_sesion": 10,
                "id_letra_objetivo": 1,
                "id_letra_detectada": 1,
                "confianza": Decimal("0.9500"),
                "es_correcto": True,
                "fecha_resultado": fecha,
            },
            {
                "id_resultado": 42,
                "id_sesion": 10,
                "id_letra_objetivo": 1,
                "id_letra_detectada": 2,
                "confianza": Decimal("0.8000"),
                "es_correcto": False,
                "fecha_resultado": fecha,
            },
        ]

        respuesta = self.cliente.get(
            "/resultados/sesion/10?id_usuario=999"
        )

        self.assertEqual(respuesta.status_code, 200, respuesta.text)
        contenido = respuesta.json()

        self.assertEqual(contenido["total"], 2)
        self.assertEqual(len(contenido["resultados"]), 2)
        self.assertEqual(
            [r["id_resultado"] for r in contenido["resultados"]],
            [41, 42],
        )
        self.assertEqual(
            [r["id_sesion"] for r in contenido["resultados"]],
            [10, 10],
        )
        self.assertEqual(
            [r["confianza"] for r in contenido["resultados"]],
            [0.95, 0.80],
        )
        self.assertEqual(
            [r["es_correcto"] for r in contenido["resultados"]],
            [True, False],
        )

        fecha_recibida = datetime.fromisoformat(
            contenido["resultados"][0]["fecha_resultado"].replace(
                "Z", "+00:00"
            )
        )
        self.assertEqual(fecha_recibida, fecha)

        self.servicio.assert_called_once_with(
            id_usuario=9,
            id_sesion=10,
        )

    def test_sesion_sin_resultados_devuelve_lista_vacia(self):
        self.autenticar()
        self.servicio.return_value = []

        respuesta = self.cliente.get("/resultados/sesion/10")

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            respuesta.json(),
            {"total": 0, "resultados": []},
        )
        self.servicio.assert_called_once_with(
            id_usuario=9,
            id_sesion=10,
        )

    def test_rechaza_solicitud_sin_autenticacion(self):
        respuesta = self.cliente.get("/resultados/sesion/10")

        self.assertEqual(respuesta.status_code, 401)
        self.assertEqual(
            respuesta.headers.get("WWW-Authenticate"),
            "Bearer",
        )
        self.servicio.assert_not_called()

    def test_rechaza_identificadores_invalidos(self):
        self.autenticar()

        for identificador in ("0", "-1", "abc", "1.5"):
            with self.subTest(id_sesion=identificador):
                respuesta = self.cliente.get(
                    f"/resultados/sesion/{identificador}"
                )

                self.assertEqual(
                    respuesta.status_code,
                    422,
                    respuesta.text,
                )
                self.servicio.assert_not_called()

    def test_devuelve_errores_de_pertenencia_y_existencia(self):
        self.autenticar()

        casos = [
            (
                SesionNoEncontradaError("La sesión no existe"),
                404,
            ),
            (
                UsuarioSesionError(
                    "La sesión no pertenece al usuario"
                ),
                403,
            ),
        ]

        for error, codigo in casos:
            with self.subTest(error=type(error).__name__):
                self.servicio.reset_mock()
                self.servicio.side_effect = error

                respuesta = self.cliente.get(
                    "/resultados/sesion/10"
                )

                self.assertEqual(respuesta.status_code, codigo)
                self.assertEqual(
                    respuesta.json(),
                    {"detail": str(error)},
                )
                self.servicio.assert_called_once_with(
                    id_usuario=9,
                    id_sesion=10,
                )

    @patch("app.routes.resultados.logger")
    def test_error_interno_no_expone_detalles(self, logger):
        self.autenticar()
        self.servicio.side_effect = RuntimeError(
            "Detalle privado de PostgreSQL"
        )

        respuesta = self.cliente.get("/resultados/sesion/10")

        self.assertEqual(respuesta.status_code, 500)
        self.assertEqual(
            respuesta.json(),
            {"detail": "No fue posible consultar los resultados"},
        )
        self.assertNotIn("Detalle privado", respuesta.text)
        logger.exception.assert_called_once()


if __name__ == "__main__":
    unittest.main()