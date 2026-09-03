import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.security import crear_token_acceso
from app.services.autenticacion_service import (
    autenticar_usuario,
    generar_hash_contrasena
)


class TestServicioAutenticacion(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.contrasena = "ClaveSeguraDePrueba123!"
        cls.hash_valido = generar_hash_contrasena(
            cls.contrasena
        )

        cls.usuario_con_hash = {
            "id_usuario": 2,
            "nombre": "Administrador de prueba",
            "correo": "admin.prueba@signia.local",
            "contrasena_hash": cls.hash_valido,
            "rol": "administrador"
        }

    @patch(
        "app.services.autenticacion_service."
        "obtener_usuario_por_correo"
    )
    def test_autentica_credenciales_correctas(
        self,
        obtener_usuario_simulado
    ):
        obtener_usuario_simulado.return_value = (
            self.usuario_con_hash
        )

        usuario = autenticar_usuario(
            "admin.prueba@signia.local",
            self.contrasena
        )

        self.assertIsNotNone(usuario)
        self.assertEqual(usuario["id_usuario"], 2)
        self.assertEqual(usuario["rol"], "administrador")
        self.assertNotIn("contrasena_hash", usuario)

    @patch(
        "app.services.autenticacion_service."
        "obtener_usuario_por_correo"
    )
    def test_rechaza_contrasena_incorrecta(
        self,
        obtener_usuario_simulado
    ):
        obtener_usuario_simulado.return_value = (
            self.usuario_con_hash
        )

        usuario = autenticar_usuario(
            "admin.prueba@signia.local",
            "clave-incorrecta"
        )

        self.assertIsNone(usuario)

    @patch(
        "app.services.autenticacion_service."
        "obtener_usuario_por_correo"
    )
    def test_controla_hash_no_utilizable(
        self,
        obtener_usuario_simulado
    ):
        usuario = dict(self.usuario_con_hash)
        usuario["contrasena_hash"] = (
            "HASH_DE_PRUEBA_NO_UTILIZABLE"
        )

        obtener_usuario_simulado.return_value = usuario

        resultado = autenticar_usuario(
            "admin.prueba@signia.local",
            self.contrasena
        )

        self.assertIsNone(resultado)


class TestRutasAutenticacion(unittest.TestCase):

    def setUp(self):
        self.cliente = TestClient(app)

        self.usuario = {
            "id_usuario": 2,
            "nombre": "Administrador de prueba",
            "correo": "admin.prueba@signia.local",
            "rol": "administrador"
        }

    def test_login_exitoso(self):
        with patch(
            "app.routes.autenticacion.autenticar_usuario",
            return_value=self.usuario
        ), patch(
            "app.routes.autenticacion.crear_token_acceso",
            return_value="token-de-prueba"
        ):
            respuesta = self.cliente.post(
                "/auth/login",
                json={
                    "correo": "admin.prueba@signia.local",
                    "contrasena": "ClaveSeguraDePrueba123!"
                }
            )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            respuesta.json(),
            {
                "access_token": "token-de-prueba",
                "token_type": "bearer",
                "usuario": self.usuario
            }
        )

    @patch(
        "app.routes.autenticacion.autenticar_usuario",
        return_value=None
    )
    def test_login_rechaza_credenciales_invalidas(
        self,
        autenticar_simulado
    ):
        respuesta = self.cliente.post(
            "/auth/login",
            json={
                "correo": "admin.prueba@signia.local",
                "contrasena": "incorrecta"
            }
        )

        self.assertEqual(respuesta.status_code, 401)
        self.assertEqual(
            respuesta.json(),
            {
                "detail": "Correo o contraseña incorrectos"
            }
        )

    @patch(
        "app.routes.autenticacion.autenticar_usuario"
    )
    def test_login_controla_error_de_base_de_datos(
        self,
        autenticar_simulado
    ):
        autenticar_simulado.side_effect = Exception(
            "Error simulado de conexión"
        )

        respuesta = self.cliente.post(
            "/auth/login",
            json={
                "correo": "admin.prueba@signia.local",
                "contrasena": "cualquier-clave"
            }
        )

        self.assertEqual(respuesta.status_code, 500)
        self.assertEqual(
            respuesta.json(),
            {"detail": "No fue posible iniciar sesión"}
        )

    def test_login_controla_error_al_generar_token(self):
        with patch(
            "app.routes.autenticacion.autenticar_usuario",
            return_value=self.usuario
        ), patch(
            "app.routes.autenticacion.crear_token_acceso",
            side_effect=Exception(
                "Error simulado al generar token"
            )
        ):
            respuesta = self.cliente.post(
                "/auth/login",
                json={
                    "correo": "admin.prueba@signia.local",
                    "contrasena": "cualquier-clave"
                }
            )

        self.assertEqual(respuesta.status_code, 500)
        self.assertEqual(
            respuesta.json(),
            {"detail": "No fue posible iniciar sesión"}
        )

    def test_me_rechaza_peticion_sin_token(self):
        respuesta = self.cliente.get("/auth/me")

        self.assertEqual(respuesta.status_code, 401)
        self.assertEqual(
            respuesta.json(),
            {
                "detail": (
                    "No fue posible validar las credenciales"
                )
            }
        )

    def test_me_rechaza_token_invalido(self):
        with patch.dict(
            os.environ,
            {
                "JWT_SECRET": "clave-secreta-de-prueba",
                "JWT_EXPIRE_MINUTES": "60"
            }
        ):
            respuesta = self.cliente.get(
                "/auth/me",
                headers={
                    "Authorization": "Bearer token-invalido"
                }
            )

        self.assertEqual(respuesta.status_code, 401)

    @patch(
        "app.security.obtener_usuario_por_id"
    )
    def test_me_devuelve_usuario_autenticado(
        self,
        obtener_usuario_simulado
    ):
        obtener_usuario_simulado.return_value = self.usuario

        with patch.dict(
            os.environ,
            {
                "JWT_SECRET": "clave-secreta-de-prueba",
                "JWT_EXPIRE_MINUTES": "60"
            }
               ):
            token = crear_token_acceso(2)

            respuesta = self.cliente.get(
                "/auth/me",
                headers={
                    "Authorization": f"Bearer {token}"
                }
            )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json(), self.usuario)
        obtener_usuario_simulado.assert_called_once_with(2)


if __name__ == "__main__":
    unittest.main()