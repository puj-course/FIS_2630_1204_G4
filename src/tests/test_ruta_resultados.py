import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.security import obtener_usuario_actual


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


if __name__ == "__main__":
    unittest.main()