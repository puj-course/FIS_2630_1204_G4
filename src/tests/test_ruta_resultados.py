import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.security import obtener_usuario_actual
from app.services.resultados_service import (
    LetraNoEncontradaError,
    SesionNoEncontradaError,
    UsuarioSesionError,
)


class TestRutaResultados(unittest.TestCase):
    def setUp(self):
        overrides_anteriores = app.dependency_overrides.copy()
        app.dependency_overrides.clear()
        self.addCleanup(self.restaurar_overrides, overrides_anteriores)

        self.cliente = TestClient(app)
        self.addCleanup(self.cliente.close)

        self.usuario = {
            "id_usuario": 9,
            "nombre": "Usuario de prueba",
            "correo": "prueba@signia.local",
            "rol": "usuario",
        }

        self.datos = {
            "id_sesion": 10,
            "id_letra_objetivo": 1,
            "id_letra_detectada": 1,
            "confianza": 0.95,
        }

    def restaurar_overrides(self, anteriores):
        app.dependency_overrides.clear()
        app.dependency_overrides.update(anteriores)

    def autenticar(self):
        app.dependency_overrides[obtener_usuario_actual] = (
            lambda: self.usuario
        )

    @patch("app.routes.resultados.registrar_resultado")
    def test_registra_con_usuario_autenticado(self, servicio):
        self.autenticar()

        servicio.return_value = {
            "id_resultado": 20,
            **self.datos,
            "es_correcto": True,
            "fecha_resultado": datetime.now(timezone.utc),
        }

        respuesta = self.cliente.post(
            "/resultados?id_usuario=999",
            json=self.datos,
        )

        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(
            respuesta.json()["mensaje"],
            "Resultado registrado correctamente",
        )
        self.assertEqual(
            respuesta.json()["resultado"]["id_sesion"],
            10,
        )
        self.assertIs(
            respuesta.json()["resultado"]["es_correcto"],
            True,
        )
        servicio.assert_called_once_with(
            id_usuario=9,
            **self.datos,
        )

    @patch("app.routes.resultados.registrar_resultado")
    def test_rechaza_solicitud_sin_autenticacion(self, servicio):
        respuesta = self.cliente.post(
            "/resultados",
            json=self.datos,
        )

        self.assertEqual(respuesta.status_code, 401)
        servicio.assert_not_called()

    @patch("app.routes.resultados.registrar_resultado")
    def test_rechaza_datos_invalidos(self, servicio):
        self.autenticar()

        casos = [
            ("sesion cero", {**self.datos, "id_sesion": 0}),
            ("sesion texto", {**self.datos, "id_sesion": "10"}),
            ("objetivo negativo", {
                **self.datos,
                "id_letra_objetivo": -1,
            }),
            ("detectada booleana", {
                **self.datos,
                "id_letra_detectada": True,
            }),
            ("confianza alta", {**self.datos, "confianza": 1.1}),
            ("confianza texto", {**self.datos, "confianza": "0.95"}),
            ("usuario adicional", {**self.datos, "id_usuario": 999}),
            ("acierto adicional", {**self.datos, "es_correcto": True}),
            ("cuerpo lista", []),
        ]

        for campo in self.datos:
            incompleto = self.datos.copy()
            del incompleto[campo]
            casos.append((f"sin {campo}", incompleto))

        for nombre, datos in casos:
            with self.subTest(caso=nombre):
                respuesta = self.cliente.post(
                    "/resultados",
                    json=datos,
                )

                self.assertEqual(
                    respuesta.status_code,
                    422,
                    respuesta.text,
                )
                servicio.assert_not_called()
    @patch("app.routes.resultados.registrar_resultado")
    def test_devuelve_errores_de_sesion_y_letras(self, servicio):
        self.autenticar()

        casos = [
            (
                SesionNoEncontradaError("La sesión no existe"),
                404,
                "La sesión no existe",
            ),
            (
                UsuarioSesionError(
                    "La sesión no pertenece al usuario"
                ),
                403,
                "La sesión no pertenece al usuario",
            ),
            (
                LetraNoEncontradaError("Alguna letra no existe"),
                404,
                "Alguna letra no existe",
            ),
        ]

        for error, codigo, detalle in casos:
            with self.subTest(error=type(error).__name__):
                servicio.reset_mock()
                servicio.side_effect = error

                respuesta = self.cliente.post(
                    "/resultados",
                    json=self.datos,
                )

                self.assertEqual(
                    respuesta.status_code,
                    codigo,
                    respuesta.text,
                )
                self.assertEqual(
                    respuesta.json(),
                    {"detail": detalle},
                )
                servicio.assert_called_once_with(
                    id_usuario=self.usuario["id_usuario"],
                    **self.datos,
                )

    @patch("app.routes.resultados.logger")
    @patch("app.routes.resultados.registrar_resultado")
    def test_error_interno_devuelve_mensaje_generico(
        self,
        servicio,
        logger,
    ):
        self.autenticar()
        servicio.side_effect = RuntimeError(
            "Detalle interno de conexión a PostgreSQL"
        )

        respuesta = self.cliente.post(
            "/resultados",
            json=self.datos,
        )

        self.assertEqual(respuesta.status_code, 500)
        self.assertEqual(
            respuesta.json(),
            {"detail": "No fue posible registrar el resultado"},
        )
        self.assertNotIn(
            "Detalle interno",
            respuesta.text,
        )
        servicio.assert_called_once_with(
            id_usuario=self.usuario["id_usuario"],
            **self.datos,
        )
        logger.exception.assert_called_once()

if __name__ == "__main__":
    unittest.main()