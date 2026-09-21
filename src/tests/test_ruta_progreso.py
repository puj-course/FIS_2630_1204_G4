import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.security import obtener_usuario_actual
from app.services.progreso_service import (
    LetraNoEncontradaError,
    ProgresoNoEncontradoError,
    UsuarioNoEncontradoError,
)


class TestRutaProgreso(unittest.TestCase):

    def setUp(self):
        # Conserva las dependencias originales al terminar cada prueba
        dependencias = patch.dict(
            app.dependency_overrides,
            {},
            clear=True,
        )
        dependencias.start()
        self.addCleanup(dependencias.stop)

        self.cliente = TestClient(app)
        self.addCleanup(self.cliente.close)

        registro = patch(
            "app.routes.progreso.registrar_progreso"
        )
        self.registrar = registro.start()
        self.addCleanup(registro.stop)

        actualizacion = patch(
            "app.routes.progreso.actualizar_estado_progreso"
        )
        self.actualizar = actualizacion.start()
        self.addCleanup(actualizacion.stop)

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

    def crear_progreso(self, id_usuario=9, dominada=True):
        return {
            "id_progreso": 10,
            "id_usuario": id_usuario,
            "id_letra": 1,
            "cantidad_intentos": 0,
            "cantidad_aciertos": 0,
            "dominada": dominada,
            "fecha_ultima_practica": None,
            "fecha_actualizacion": datetime(
                2026,
                9,
                17,
                tzinfo=timezone.utc,
            ),
        }

    def test_registra_para_el_usuario_autenticado(self):
        for id_usuario in (9, 15):
            with self.subTest(id_usuario=id_usuario):
                self.registrar.reset_mock()
                self.autenticar_usuario(id_usuario)

                self.registrar.return_value = (
                    self.crear_progreso(id_usuario)
                )

                respuesta = self.cliente.post(
                    "/progreso?id_usuario=999",
                    json={"id_letra": 1},
                )

                self.assertEqual(respuesta.status_code, 200)

                cuerpo = respuesta.json()

                self.assertEqual(
                    cuerpo["mensaje"],
                    "Letra registrada como aprendida",
                )
                self.assertEqual(
                    cuerpo["progreso"]["id_usuario"],
                    id_usuario,
                )
                self.assertTrue(
                    cuerpo["progreso"]["dominada"]
                )

                self.registrar.assert_called_once_with(
                    id_usuario=id_usuario,
                    id_letra=1,
                )
                self.actualizar.assert_not_called()

    def test_actualiza_para_el_usuario_autenticado(self):
        for id_usuario in (9, 15):
            for dominada in (True, False):
                with self.subTest(
                    id_usuario=id_usuario,
                    dominada=dominada,
                ):
                    self.actualizar.reset_mock()
                    self.autenticar_usuario(id_usuario)

                    self.actualizar.return_value = (
                        self.crear_progreso(
                            id_usuario,
                            dominada,
                        )
                    )

                    respuesta = self.cliente.patch(
                        "/progreso/1?id_usuario=999",
                        json={"dominada": dominada},
                    )

                    self.assertEqual(
                        respuesta.status_code,
                        200,
                    )

                    cuerpo = respuesta.json()

                    self.assertEqual(
                        cuerpo["mensaje"],
                        "Estado de aprendizaje actualizado correctamente",
                    )
                    self.assertEqual(
                        cuerpo["progreso"]["id_usuario"],
                        id_usuario,
                    )
                    self.assertEqual(
                        cuerpo["progreso"]["dominada"],
                        dominada,
                    )

                    self.actualizar.assert_called_once_with(
                        id_usuario=id_usuario,
                        id_letra=1,
                        dominada=dominada,
                    )
                    self.registrar.assert_not_called()

    def test_rechaza_solicitudes_sin_autenticacion(self):
        casos = [
            ("POST", "/progreso", {"id_letra": 1}),
            ("PATCH", "/progreso/1", {"dominada": True}),
        ]

        for metodo, ruta, datos in casos:
            with self.subTest(metodo=metodo):
                respuesta = self.cliente.request(
                    metodo,
                    ruta,
                    json=datos,
                )

                self.assertEqual(respuesta.status_code, 401)
                self.assertEqual(
                    respuesta.headers.get("www-authenticate"),
                    "Bearer",
                )

        self.registrar.assert_not_called()
        self.actualizar.assert_not_called()

    def test_rechaza_datos_invalidos_al_registrar(self):
        self.autenticar_usuario()

        casos = [
            {},
            {"id_letra": 0},
            {"id_letra": -1},
            {"id_letra": "1"},
            {"id_letra": True},
            {"id_letra": 1, "id_usuario": 999},
        ]

        for datos in casos:
            with self.subTest(datos=datos):
                respuesta = self.cliente.post(
                    "/progreso",
                    json=datos,
                )

                self.assertEqual(respuesta.status_code, 422)

        self.registrar.assert_not_called()
        self.actualizar.assert_not_called()

    def test_rechaza_datos_invalidos_al_actualizar(self):
        self.autenticar_usuario()

        casos = [
            {},
            {"dominada": "true"},
            {"dominada": "false"},
            {"dominada": 1},
            {"dominada": 0},
            {"dominada": None},
            {"dominada": True, "id_usuario": 999},
        ]

        for datos in casos:
            with self.subTest(datos=datos):
                respuesta = self.cliente.patch(
                    "/progreso/1",
                    json=datos,
                )

                self.assertEqual(respuesta.status_code, 422)

        self.registrar.assert_not_called()
        self.actualizar.assert_not_called()

    def test_rechaza_identificador_invalido_en_la_ruta(self):
        self.autenticar_usuario()

        for id_letra in ("0", "-1", "abc"):
            with self.subTest(id_letra=id_letra):
                respuesta = self.cliente.patch(
                    f"/progreso/{id_letra}",
                    json={"dominada": True},
                )

                self.assertEqual(respuesta.status_code, 422)

        self.registrar.assert_not_called()
        self.actualizar.assert_not_called()

    def test_responde_404_para_registros_inexistentes(self):
        self.autenticar_usuario()

        casos = [
            (
                "POST",
                "/progreso",
                {"id_letra": 1},
                self.registrar,
                UsuarioNoEncontradoError("El usuario no existe"),
            ),
            (
                "POST",
                "/progreso",
                {"id_letra": 1},
                self.registrar,
                LetraNoEncontradaError("La letra no existe"),
            ),
            (
                "PATCH",
                "/progreso/1",
                {"dominada": True},
                self.actualizar,
                ProgresoNoEncontradoError(
                    "No existe progreso para este usuario y esta letra"
                ),
            ),
        ]

        for metodo, ruta, datos, servicio, error in casos:
            with self.subTest(error=type(error).__name__):
                servicio.side_effect = error

                respuesta = self.cliente.request(
                    metodo,
                    ruta,
                    json=datos,
                )

                self.assertEqual(respuesta.status_code, 404)
                self.assertEqual(
                    respuesta.json(),
                    {"detail": str(error)},
                )

    def test_controla_errores_de_almacenamiento(self):
        self.autenticar_usuario()

        casos = [
            (
                "POST",
                "/progreso",
                {"id_letra": 1},
                self.registrar,
                "No fue posible registrar el progreso",
            ),
            (
                "PATCH",
                "/progreso/1",
                {"dominada": False},
                self.actualizar,
                "No fue posible actualizar el progreso",
            ),
        ]

        for metodo, ruta, datos, servicio, mensaje in casos:
            with self.subTest(metodo=metodo):
                servicio.side_effect = RuntimeError(
                    "Detalle interno de prueba"
                )

                with self.assertLogs(
                    "app.routes.progreso",
                    level="ERROR",
                ):
                    respuesta = self.cliente.request(
                        metodo,
                        ruta,
                        json=datos,
                    )

                self.assertEqual(respuesta.status_code, 500)
                self.assertEqual(
                    respuesta.json(),
                    {"detail": mensaje},
                )
                self.assertNotIn(
                    "Detalle interno de prueba",
                    respuesta.text,
                )


if __name__ == "__main__":
    unittest.main()