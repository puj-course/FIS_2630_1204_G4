import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.security import obtener_usuario_actual, requerir_administrador
from app.services import usuarios_service as servicio_usuarios
from app.services.progreso_service import UsuarioNoEncontradoError
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

    @patch("app.routes.usuarios.listar_usuarios")
    def test_lista_usuarios_sin_filtro(self,servicio_simulado):
        servicio_simulado.return_value = [
            {
                "id_usuario": 1,
                "nombre": "Usuario Uno",
                "correo": "uno@signia.local",
                "rol": "usuario",
                "fecha_creacion": "2026-01-01T00:00:00",
                "activo": True
            }
        ]

        respuesta = self.cliente.get("/usuarios")

        self.assertEqual(respuesta.status_code,200)
        self.assertEqual(len(respuesta.json()), 1)
        servicio_simulado.assert_called_once_with(None)

    @patch("app.routes.usuarios.listar_usuarios")
    def test_lista_usuarios_con_filtro(self, servicio_simulado):
        servicio_simulado.return_value = []

        respuesta = self.cliente.get(
            "/usuarios",
            params={"buscar": "ana"}
        )

        self.assertEqual(respuesta.status_code, 200)
        servicio_simulado.assert_called_once_with("ana")

    @patch("app.routes.usuarios.listar_usuarios")
    def test_listar_usuarios_no_expone_datos_sensibles(
        self,
        servicio_simulado
    ):
        servicio_simulado.return_value = [
            {
                "id_usuario": 1,
                "nombre": "Usuario Uno",
                "correo": "uno@signia.local",
                "rol": "usuario",
                "fecha_creacion": "2026-01-01T00:00:00",
                "activo": True
            }
        ]

        respuesta = self.cliente.get("/usuarios")

        self.assertNotIn("contrasena_hash", respuesta.json()[0])

    def test_listar_usuarios_rechaza_usuario_sin_permisos(self):
        app.dependency_overrides.pop(requerir_administrador, None)
        app.dependency_overrides[obtener_usuario_actual] = lambda: {
            "id_usuario": 4,
            "nombre": "Usuario",
            "correo": "usuario@signia.local",
            "rol": "usuario"
        }

        respuesta = self.cliente.get("/usuarios")

        self.assertEqual(respuesta.status_code, 403)

    @patch("app.routes.usuarios.listar_usuarios")
    def test_listar_usuarios_controla_error_inesperado(
        self,
        servicio_simulado
    ):
        servicio_simulado.side_effect = Exception(
            "Error simulado de DB"
        )

        respuesta = self.cliente.get("/usuarios")

        self.assertEqual(respuesta.status_code, 500)
        self.assertEqual(
            respuesta.json(),
            {"detail": "No fue posible obtener la lista de los usuarios"}
        )

    @patch("app.routes.usuarios.reactivar_usuario")
    def test_reactiva_un_usuario(self, servicio_simulado):
        servicio_simulado.return_value = {
            "id_usuario": 5,
            "nombre": "Usuario Prueba",
            "correo": "usuario@signia.local",
            "rol": "usuario",
            "activo": True
        }

        respuesta = self.cliente.patch("/usuarios/5/reactivar")

        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.json()["activo"])
        servicio_simulado.assert_called_once_with(5)

    @patch("app.routes.usuarios.reactivar_usuario")
    def test_reactivar_responde_404_si_no_existe(
        self,
        servicio_simulado
    ):
        servicio_simulado.return_value = None

        respuesta = self.cliente.patch("/usuarios/999/reactivar")

        self.assertEqual(respuesta.status_code, 404)
        self.assertEqual(
            respuesta.json(),
            {"detail": "El usuario no existe"}
        )

    def test_no_puede_reactivar_su_propia_cuenta(self):
        respuesta = self.cliente.patch("/usuarios/1/reactivar")

        self.assertEqual(respuesta.status_code,400)
        self.assertEqual(
            respuesta.json(),
            {"detail": "No se puede reactivar su propia cuenta"}
        )

    def test_reactivar_rechaza_usuario_sin_permisos(self):
        app.dependency_overrides.pop(requerir_administrador, None)
        app.dependency_overrides[obtener_usuario_actual] = lambda: {
            "id_usuario": 4,
            "nombre": "Usuario",
            "correo": "usuarios@signia.local",
            "rol": "usuario"
        }

        respuesta = self.cliente.patch("/usuarios/5/reactivar")

        self.assertEqual(respuesta.status_code, 403)

    @patch("app.routes.usuarios.consultar_resumen_progreso_usuario")
    def test_consulta_el_progreso_de_un_usuario(
        self,            
        servicio_simulado
    ):
        servicio_simulado.return_value = {
            "total_intentos": 20, 
            "total_aciertos": 15,                
            "letras_dominadas": 3,
            "letras_pendientes": 23
        }

        respuesta = self.cliente.get("/usuarios/5/progreso")

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            respuesta.json(),
            {
                "total_intentos": 20, 
                "total_aciertos": 15,
                "letras_dominadas": 3,                                
                "letras_pendientes": 23
            }
        )
        servicio_simulado.assert_called_once_with(5)

    @patch("app.routes.usuarios.consultar_resumen_progreso_usuario")
    def test_progreso_responde_404_si_no_existe(
        self,
        servicio_simulado
    ):
        servicio_simulado.side_effect = UsuarioNoEncontradoError(
            "El usuario no existe"
        )

        respuesta = self.cliente.get("/usuarios/999/progreso")

        self.assertEqual(respuesta.status_code, 404)
        self.assertEqual(
            respuesta.json(),
            {"detail": "El usuario no existe"}
        )

    def test_progreso_rechaza_usuario_sin_permisos(self):
        app.dependency_overrides.pop(requerir_administrador, None)
        app.dependency_overrides[obtener_usuario_actual] = lambda: {
            "id_usuario": 4,
            "nombre": "Usuario",
            "correo": "usuario@signia.local",
            "rol": "usuario"
        }

        respuesta = self.cliente.get("/usuarios/5/progreso")

        self.assertEqual(respuesta.status_code, 403)

class TestServicioUsuariosCobertura(unittest.TestCase):
    """Pruebas unitarias de las operaciones del servicio de usuarios."""

    def setUp(self):
        # Simula la conexión a PostgreSQL.
        parche_conexion = patch(
            "app.services.usuarios_service.obtener_conexion"
        )

        self.obtener_conexion = parche_conexion.start()
        self.addCleanup(parche_conexion.stop)

        self.conexion = (
            self.obtener_conexion.return_value
            .__enter__.return_value
        )

        self.cursor = (
            self.conexion.cursor.return_value
            .__enter__.return_value
        )

    def test_crear_usuario_correctamente(self):
        # Arrange
        usuario_esperado = {
            "id_usuario": 7,
            "nombre": "Ana",
            "correo": "ana@example.com",
            "rol": "usuario",
        }

        self.cursor.fetchone.return_value = usuario_esperado

        with patch(
            "app.services.usuarios_service.generar_hash_contrasena",
            return_value="hash-simulado",
        ) as generar_hash:

            # Act
            resultado = servicio_usuarios.crear_usuario(
                nombre=" Ana ",
                correo=" ANA@EXAMPLE.COM ",
                contrasena="Contrasena123",
                rol="usuario",
            )

        # Assert
        self.assertEqual(resultado, usuario_esperado)

        generar_hash.assert_called_once_with(
            "Contrasena123"
        )

        self.cursor.execute.assert_called_once()

        consulta, parametros = self.cursor.execute.call_args.args

        self.assertIn("INSERT INTO usuarios", consulta)

        self.assertEqual(
            parametros,
            (
                "Ana",
                "ana@example.com",
                "hash-simulado",
                "usuario",
            ),
        )

    def test_crear_usuario_rechaza_correo_duplicado(self):
        # Arrange
        from psycopg.errors import UniqueViolation

        self.cursor.execute.side_effect = UniqueViolation(
            "Correo duplicado"
        )

        with patch(
            "app.services.usuarios_service.generar_hash_contrasena",
            return_value="hash-simulado",
        ):
            # Act / Assert
            with self.assertRaises(
                servicio_usuarios.CorreoYaRegistradoError
            ):
                servicio_usuarios.crear_usuario(
                    "Ana",
                    "ana@example.com",
                    "Contrasena123",
                    "usuario",
                )

    def test_listar_usuarios_sin_filtro(self):
        # Arrange
        usuarios_esperados = [
            {
                "id_usuario": 1,
                "nombre": "Ana",
                "correo": "ana@example.com",
            },
            {
                "id_usuario": 2,
                "nombre": "Pedro",
                "correo": "pedro@example.com",
            },
        ]

        self.cursor.fetchall.return_value = usuarios_esperados

        # Act
        resultado = servicio_usuarios.listar_usuarios()

        # Assert
        self.assertEqual(resultado, usuarios_esperados)

        self.cursor.execute.assert_called_once()

        consulta = self.cursor.execute.call_args.args[0]

        self.assertIn("SELECT", consulta)
        self.assertIn("FROM usuarios", consulta)
        self.assertIn("ORDER BY nombre", consulta)
        self.assertNotIn("ILIKE", consulta)

    def test_listar_usuarios_con_filtro(self):
        # Arrange
        usuarios_esperados = [
            {
                "id_usuario": 1,
                "nombre": "Ana",
                "correo": "ana@example.com",
            }
        ]

        self.cursor.fetchall.return_value = usuarios_esperados

        # Act
        resultado = servicio_usuarios.listar_usuarios(
            buscar="ana"
        )

        # Assert
        self.assertEqual(resultado, usuarios_esperados)

        self.cursor.execute.assert_called_once()

        consulta, parametros = self.cursor.execute.call_args.args

        self.assertIn("ILIKE", consulta)

        self.assertEqual(
            parametros,
            ("%ana%", "%ana%"),
        )

    def test_cambiar_rol_usuario(self):
        # Arrange
        usuario_esperado = {
            "id_usuario": 7,
            "nombre": "Ana",
            "correo": "ana@example.com",
            "rol": "administrador",
        }

        self.cursor.fetchone.return_value = usuario_esperado

        # Act
        resultado = servicio_usuarios.cambiar_rol(
            id_usuario=7,
            nuevo_rol="administrador",
        )

        # Assert
        self.assertEqual(resultado, usuario_esperado)

        self.cursor.execute.assert_called_once()

        consulta, parametros = self.cursor.execute.call_args.args

        self.assertIn("UPDATE usuarios", consulta)
        self.assertIn("SET rol = %s", consulta)

        self.assertEqual(
            parametros,
            ("administrador", 7),
        )

    def test_desactivar_usuario(self):
        # Arrange
        usuario_esperado = {
            "id_usuario": 7,
            "nombre": "Ana",
            "correo": "ana@example.com",
            "rol": "usuario",
            "activo": False,
        }

        self.cursor.fetchone.return_value = usuario_esperado

        # Act
        resultado = servicio_usuarios.desactivar_usuario(
            id_usuario=7
        )

        # Assert
        self.assertEqual(resultado, usuario_esperado)

        self.cursor.execute.assert_called_once()

        consulta, parametros = self.cursor.execute.call_args.args

        self.assertIn("UPDATE usuarios", consulta)
        self.assertIn("SET activo = FALSE", consulta)

        self.assertEqual(parametros, (7,))

    def test_reactivar_usuario(self):
        # Arrange
        usuario_esperado = {
            "id_usuario": 7,
            "nombre": "Ana",
            "correo": "ana@example.com",
            "rol": "usuario",
            "activo": True,
        }

        self.cursor.fetchone.return_value = usuario_esperado

        # Act
        resultado = servicio_usuarios.reactivar_usuario(
            id_usuario=7
        )

        # Assert
        self.assertEqual(resultado, usuario_esperado)

        self.cursor.execute.assert_called_once()

        consulta, parametros = self.cursor.execute.call_args.args

        self.assertIn("UPDATE usuarios", consulta)
        self.assertIn("SET activo = TRUE", consulta)

        self.assertEqual(parametros, (7,))

if __name__ == "__main__":
    unittest.main()
