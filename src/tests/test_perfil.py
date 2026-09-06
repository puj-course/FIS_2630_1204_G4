import os
import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.security import (
    crear_token_acceso,
    obtener_usuario_actual
)
from app.services.perfil_service import obtener_progreso_usuario


class TestServicioPerfil(unittest.TestCase):

    @patch(
        "app.services.perfil_service.obtener_conexion"
    )
    def test_calcula_porcentaje_de_progreso(
        self,
        obtener_conexion_simulada
    ):
        conexion = MagicMock()
        cursor = MagicMock()

        obtener_conexion_simulada.return_value.__enter__.return_value = (
            conexion
        )
        conexion.cursor.return_value.__enter__.return_value = cursor

        cursor.fetchone.return_value = {
            "total_letras": 26,
            "letras_iniciadas": 5,
            "letras_dominadas": 3,
            "cantidad_intentos": 20,
            "cantidad_aciertos": 15
        }

        resultado = obtener_progreso_usuario(7)

        self.assertEqual(resultado["porcentaje_progreso"], 11.54)
        self.assertEqual(resultado["letras_dominadas"], 3)
        self.assertEqual(
            cursor.execute.call_args.args[1],
            (7,)
        )

    @patch(
        "app.services.perfil_service.obtener_conexion"
    )
    def test_devuelve_cero_sin_letras_activas(
        self,
        obtener_conexion_simulada
    ):
        conexion = MagicMock()
        cursor = MagicMock()

        obtener_conexion_simulada.return_value.__enter__.return_value = (
            conexion
        )
        conexion.cursor.return_value.__enter__.return_value = cursor

        cursor.fetchone.return_value = {
            "total_letras": 0,
            "letras_iniciadas": 0,
            "letras_dominadas": 0,
            "cantidad_intentos": 0,
            "cantidad_aciertos": 0
        }

        resultado = obtener_progreso_usuario(7)

        self.assertEqual(resultado["porcentaje_progreso"], 0.0)


class TestRutaPerfil(unittest.TestCase):

    def setUp(self):
        app.dependency_overrides.clear()
        self.cliente = TestClient(app)
        self.usuario = {
            "id_usuario": 7,
            "nombre": "Usuario de prueba",
            "correo": "usuario@signia.local",
            "rol": "usuario"
        }

    def tearDown(self):
        app.dependency_overrides.clear()

    def autenticar_usuario(self):
        app.dependency_overrides[
            obtener_usuario_actual
        ] = lambda: self.usuario

    def test_rechaza_peticion_sin_token(self):
        respuesta = self.cliente.get("/perfil")

        self.assertEqual(respuesta.status_code, 401)

    @patch(
        "app.security.obtener_usuario_por_id",
        return_value=None
    )
    def test_rechaza_usuario_inexistente(
        self,
        _obtener_usuario_simulado
    ):
        with patch.dict(
            os.environ,
            {
                "JWT_SECRET": "clave-secreta-de-prueba",
                "JWT_EXPIRE_MINUTES": "60"
            }
        ):
            token = crear_token_acceso(999)

            respuesta = self.cliente.get(
                "/perfil",
                headers={
                    "Authorization": f"Bearer {token}"
                }
            )

        self.assertEqual(respuesta.status_code, 401)

    @patch(
        "app.routes.perfil.obtener_progreso_usuario"
    )
    def test_devuelve_perfil_del_usuario_autenticado(
        self,
        obtener_progreso_simulado
    ):
        self.autenticar_usuario()

        progreso = {
            "total_letras": 26,
            "letras_iniciadas": 5,
            "letras_dominadas": 3,
            "cantidad_intentos": 20,
            "cantidad_aciertos": 15,
            "porcentaje_progreso": 11.54
        }
        obtener_progreso_simulado.return_value = progreso

        respuesta = self.cliente.get(
            "/perfil?id_usuario=999"
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            respuesta.json(),
            {
                **self.usuario,
                "progreso": progreso
            }
        )
        obtener_progreso_simulado.assert_called_once_with(7)

    @patch(
        "app.routes.perfil.obtener_progreso_usuario"
    )
    def test_devuelve_ceros_sin_progreso(
        self,
        obtener_progreso_simulado
    ):
        self.autenticar_usuario()

        obtener_progreso_simulado.return_value = {
            "total_letras": 2,
            "letras_iniciadas": 0,
            "letras_dominadas": 0,
            "cantidad_intentos": 0,
            "cantidad_aciertos": 0,
            "porcentaje_progreso": 0.0
        }

        respuesta = self.cliente.get("/perfil")

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            respuesta.json()["progreso"]["porcentaje_progreso"],
            0.0
        )

    @patch(
        "app.routes.perfil.obtener_progreso_usuario",
        side_effect=Exception("Error simulado")
    )
    def test_controla_error_de_base_de_datos(
        self,
        _obtener_progreso_simulado
    ):
        self.autenticar_usuario()

        respuesta = self.cliente.get("/perfil")

        self.assertEqual(respuesta.status_code, 500)
        self.assertEqual(
            respuesta.json(),
            {
                "detail": "No fue posible consultar el perfil"
            }
        )


if __name__ == "__main__":
    unittest.main()