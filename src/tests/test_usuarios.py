import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.security import (
    obtener_usuario_actual,
    requerir_administrador
)
from app.services.usuarios_service import CorreoYaRegistradoError


class TestRegistroUsuarios(unittest.TestCase):

    def setUp(self):
        self.cliente = TestClient(app)
        self.administrador = {
            "id_usuario": 1,
            "nombre": "Administrador",
            "correo": "admin@signia.local",
            "rol": "administrador"
        }

        app.dependency_overrides[
            requerir_administrador
        ] = lambda: self.administrador

    def tearDown(self):
        app.dependency_overrides.clear()

    @patch("app.routes.usuarios.crear_usuario")
    def test_registra_un_usuario(self, servicio_simulado):
        usuario_creado = {
            "id_usuario": 2,
            "nombre": "Usuario Prueba",
            "correo": "usuario@signia.local",
            "rol": "usuario"
        }
        servicio_simulado.return_value = usuario_creado

        respuesta = self.cliente.post(
            "/usuarios",
            json={
                "nombre": "Usuario Prueba",
                "correo": "USUARIO@SIGNIA.LOCAL",
                "contrasena": "ClaveSegura123",
                "rol": "usuario"
            }
        )

        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(
            respuesta.json(),
            {
                "mensaje": "Usuario registrado correctamente",
                "usuario": usuario_creado
            }
        )
        self.assertNotIn(
            "contrasena",
            respuesta.json()["usuario"]
        )
        self.assertNotIn(
            "contrasena_hash",
            respuesta.json()["usuario"]
        )

        servicio_simulado.assert_called_once_with(
            nombre="Usuario Prueba",
            correo="usuario@signia.local",
            contrasena="ClaveSegura123",
            rol="usuario"
        )

    @patch("app.routes.usuarios.crear_usuario")
    def test_permite_registrar_administrador(
        self,
        servicio_simulado
    ):
        servicio_simulado.return_value = {
            "id_usuario": 3,
            "nombre": "Nuevo Administrador",
            "correo": "nuevo.admin@signia.local",
            "rol": "administrador"
        }

        respuesta = self.cliente.post(
            "/usuarios",
            json={
                "nombre": "Nuevo Administrador",
                "correo": "nuevo.admin@signia.local",
                "contrasena": "ClaveSegura456",
                "rol": "administrador"
            }
        )

        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(
            respuesta.json()["usuario"]["rol"],
            "administrador"
        )

    @patch("app.routes.usuarios.crear_usuario")
    def test_responde_409_si_el_correo_ya_existe(
        self,
        servicio_simulado
    ):
        servicio_simulado.side_effect = CorreoYaRegistradoError()

        respuesta = self.cliente.post(
            "/usuarios",
            json={
                "nombre": "Usuario Duplicado",
                "correo": "duplicado@signia.local",
                "contrasena": "ClaveSegura123",
                "rol": "usuario"
            }
        )

        self.assertEqual(respuesta.status_code, 409)
        self.assertEqual(
            respuesta.json(),
            {"detail": "El correo ya se encuentra registrado"}
        )

    def test_rechaza_un_rol_invalido(self):
        respuesta = self.cliente.post(
            "/usuarios",
            json={
                "nombre": "Usuario Prueba",
                "correo": "usuario@signia.local",
                "contrasena": "ClaveSegura123",
                "rol": "superusuario"
            }
        )

        self.assertEqual(respuesta.status_code, 422)

    def test_rechaza_campos_obligatorios_faltantes(self):
        respuesta = self.cliente.post(
            "/usuarios",
            json={
                "nombre": "Usuario Prueba"
            }
        )

        self.assertEqual(respuesta.status_code, 422)

    def test_requiere_autenticacion(self):
        app.dependency_overrides.pop(
            requerir_administrador,
            None
        )

        respuesta = self.cliente.post(
            "/usuarios",
            json={
                "nombre": "Usuario Prueba",
                "correo": "usuario@signia.local",
                "contrasena": "ClaveSegura123",
                "rol": "usuario"
            }
        )

        self.assertEqual(respuesta.status_code, 401)

    def test_rechaza_usuario_sin_permisos(self):
        app.dependency_overrides.pop(
            requerir_administrador,
            None
        )
        app.dependency_overrides[
            obtener_usuario_actual
        ] = lambda: {
            "id_usuario": 4,
            "nombre": "Usuario",
            "correo": "usuario@signia.local",
            "rol": "usuario"
        }

        respuesta = self.cliente.post(
            "/usuarios",
            json={
                "nombre": "Otro Usuario",
                "correo": "otro@signia.local",
                "contrasena": "ClaveSegura123",
                "rol": "usuario"
            }
        )

        self.assertEqual(respuesta.status_code, 403)
        self.assertEqual(
            respuesta.json(),
            {"detail": "No tiene permisos de administrador"}
        )

    @patch("app.routes.usuarios.crear_usuario")
    def test_controla_error_inesperado(
        self,
        servicio_simulado
    ):
        servicio_simulado.side_effect = Exception(
            "Error simulado de base de datos"
        )

        respuesta = self.cliente.post(
            "/usuarios",
            json={
                "nombre": "Usuario Prueba",
                "correo": "usuario@signia.local",
                "contrasena": "ClaveSegura123",
                "rol": "usuario"
            }
        )

        self.assertEqual(respuesta.status_code, 500)
        self.assertEqual(
            respuesta.json(),
            {"detail": "No fue posible registrar el usuario"}
        )


    @patch("app.routes.autenticacion.crear_usuario")
    def test_permite_autoregistro_publico(
        self,
        servicio_simulado
    ):
        usuario_creado = {
            "id_usuario": 5,
            "nombre": "Usuario Nuevo",
            "correo": "nuevo@signia.local",
            "rol": "usuario"
        }
        servicio_simulado.return_value = usuario_creado

        respuesta = self.cliente.post(
            "/auth/registro",
            json={
                "nombre": "Usuario Nuevo",
                "correo": "NUEVO@SIGNIA.LOCAL",
                "contrasena": "ClaveSegura789"
            }
        )

        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(
            respuesta.json()["usuario"]["rol"],
            "usuario"
        )
        self.assertNotIn(
            "contrasena",
            respuesta.json()["usuario"]
        )
        self.assertNotIn(
            "contrasena_hash",
            respuesta.json()["usuario"]
        )

        servicio_simulado.assert_called_once_with(
            nombre="Usuario Nuevo",
            correo="nuevo@signia.local",
            contrasena="ClaveSegura789",
            rol="usuario"
        )

    @patch("app.routes.autenticacion.crear_usuario")
    def test_autoregistro_no_permite_elegir_rol(
        self,
        servicio_simulado
    ):
        respuesta = self.cliente.post(
            "/auth/registro",
            json={
                "nombre": "Usuario Nuevo",
                "correo": "nuevo@signia.local",
                "contrasena": "ClaveSegura789",
                "rol": "administrador"
            }
        )

        self.assertEqual(respuesta.status_code, 422)
        servicio_simulado.assert_not_called()

    @patch("app.routes.autenticacion.crear_usuario")
    def test_autoregistro_controla_correo_duplicado(
        self,
        servicio_simulado
    ):
        servicio_simulado.side_effect = CorreoYaRegistradoError()

        respuesta = self.cliente.post(
            "/auth/registro",
            json={
                "nombre": "Usuario Duplicado",
                "correo": "duplicado@signia.local",
                "contrasena": "ClaveSegura123"
            }
        )

        self.assertEqual(respuesta.status_code, 409)
        self.assertEqual(
            respuesta.json(),
            {"detail": "El correo ya se encuentra registrado"}
        )

    @patch("app.routes.autenticacion.crear_usuario")
    def test_autoregistro_controla_error_inesperado(
        self,
        servicio_simulado
    ):
        servicio_simulado.side_effect = Exception(
            "Error simulado de base de datos"
        )

        respuesta = self.cliente.post(
            "/auth/registro",
            json={
                "nombre": "Usuario Nuevo",
                "correo": "nuevo@signia.local",
                "contrasena": "ClaveSegura789"
            }
        )

        self.assertEqual(respuesta.status_code, 500)
        self.assertEqual(
            respuesta.json(),
            {"detail": "No fue posible registrar el usuario"}
        )

    def test_autoregistro_rechaza_contrasena_corta(self):
        respuesta = self.cliente.post(
            "/auth/registro",
            json={
                "nombre": "Usuario Nuevo",
                "correo": "nuevo@signia.local",
                "contrasena": "corta"
            }
        )

        self.assertEqual(respuesta.status_code, 422)


if __name__ == "__main__":
    unittest.main()