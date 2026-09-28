import os
import unittest
from uuid import uuid4

from fastapi.testclient import TestClient
from psycopg.rows import dict_row

from app.main import app
from app.security import obtener_usuario_actual
from conf.database import obtener_conexion


@unittest.skipUnless(
    os.getenv("DATABASE_URL"),
    "Se necesita DATABASE_URL para probar PostgreSQL",
)
class TestFlujoSesionesIntegracion(unittest.TestCase):

    def setUp(self):
        self.cliente = TestClient(app)

        self.id_usuario = self.crear_usuario_prueba()

        self.usuario = {
            "id_usuario": self.id_usuario,
            "nombre": "Usuario prueba",
            "correo": "prueba@signia.com",
            "rol": "usuario",
        }

        app.dependency_overrides[
            obtener_usuario_actual
        ] = lambda: self.usuario

        self.addCleanup(
            self.limpiar_datos
        )

    def crear_usuario_prueba(self):
        with obtener_conexion() as conexion:
            with conexion.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    INSERT INTO usuarios (
                        nombre,
                        correo,
                        contrasena_hash,
                        rol
                    )
                    VALUES (%s, %s, %s, 'usuario')
                    RETURNING id_usuario;
                    """,
                    (
                        "Usuario flujo sesiones",
                        f"flujo-{uuid4().hex}@signia.local",
                        "hash-prueba",
                    ),
                )

                return cursor.fetchone()["id_usuario"]

    def limpiar_datos(self):
        app.dependency_overrides.clear()

        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM usuarios
                    WHERE id_usuario = %s;
                    """,
                    (self.id_usuario,),
                )

    def test_flujo_completo_sesion_reconocimiento(self):

        crear = self.cliente.post(
            "/sesiones"
        )

        self.assertEqual(
            crear.status_code,
            201,
        )

        sesion = crear.json()["sesion"]

        id_sesion = sesion["id_sesion"]

        self.assertEqual(
            sesion["id_usuario"],
            self.id_usuario,
        )

        self.assertEqual(
            sesion["estado"],
            "activa",
        )


        consulta = self.cliente.get(
            "/sesiones"
        )

        self.assertEqual(
            consulta.status_code,
            200,
        )

        sesiones = consulta.json()["sesiones"]

        self.assertTrue(
            any(
                s["id_sesion"] == id_sesion
                for s in sesiones
            )
        )


        finalizar = self.cliente.patch(
            f"/sesiones/{id_sesion}/finalizar"
        )

        self.assertEqual(
            finalizar.status_code,
            200,
        )

        sesion_final = finalizar.json()["sesion"]

        self.assertEqual(
            sesion_final["estado"],
            "finalizada",
        )

        self.assertIsNotNone(
            sesion_final["fecha_fin"],
        )


    def test_usuario_no_puede_acceder_a_sesion_ajena(self):

        otro_usuario = self.crear_usuario_prueba()

        app.dependency_overrides[
            obtener_usuario_actual
        ] = lambda: {
            "id_usuario": otro_usuario,
            "nombre": "Otro usuario",
            "correo": "otro@signia.com",
            "rol": "usuario",
        }

        respuesta = self.cliente.patch(
            "/sesiones/999999/finalizar"
        )

        self.assertIn(
            respuesta.status_code,
            [403, 404],
        )


if __name__ == "__main__":
    unittest.main()