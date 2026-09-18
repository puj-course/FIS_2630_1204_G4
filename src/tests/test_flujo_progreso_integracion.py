import os
import unittest
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient
from psycopg.rows import dict_row

from app.main import app
from app.security import crear_token_acceso
from conf.database import obtener_conexion


@unittest.skipUnless(
    os.getenv("DATABASE_URL"),
    "Se necesita DATABASE_URL para probar PostgreSQL",
)
class TestFlujoProgresoIntegracion(unittest.TestCase):

    def setUp(self):
        self.usuarios_creados = []
        self.addCleanup(self.eliminar_datos_prueba)

        # Utiliza una clave temporal únicamente en estas pruebas.
        entorno = patch.dict(
            os.environ,
            {
                "JWT_SECRET": uuid4().hex + uuid4().hex,
                "JWT_EXPIRE_MINUTES": "60",
            },
        )
        entorno.start()
        self.addCleanup(entorno.stop)

        # Evita heredar sustituciones de autenticación de otras pruebas.
        dependencias = patch.dict(
            app.dependency_overrides,
            {},
            clear=True,
        )
        dependencias.start()
        self.addCleanup(dependencias.stop)

        self.cliente = TestClient(app)
        self.addCleanup(self.cliente.close)

        with obtener_conexion() as conexion:
            with conexion.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT
                        id_letra,
                        letra,
                        descripcion,
                        ruta_imagen
                    FROM letras
                    WHERE activa = TRUE
                    ORDER BY letra, id_letra;
                    """
                )
                self.letras = cursor.fetchall()

        if not self.letras:
            self.skipTest(
                "Se necesita al menos una letra activa"
            )

        self.id_usuario = self.crear_usuario()
        self.id_letra = self.letras[0]["id_letra"]

    def crear_usuario(self):
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
                        "Prueba flujo de progreso",
                        f"flujo-{uuid4().hex}@signia.local",
                        "hash-solo-para-pruebas",
                    ),
                )
                id_usuario = cursor.fetchone()["id_usuario"]
                self.usuarios_creados.append(id_usuario)

        return id_usuario

    def eliminar_datos_prueba(self):
        if not self.usuarios_creados:
            return

        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                for id_usuario in self.usuarios_creados:
                    cursor.execute(
                        """
                        DELETE FROM usuarios
                        WHERE id_usuario = %s;
                        """,
                        (id_usuario,),
                    )

    def cabeceras_usuario(self, id_usuario):
        token = crear_token_acceso(id_usuario)

        return {
            "Authorization": f"Bearer {token}",
        }

    def leer_progreso_sql(self, id_usuario):
        with obtener_conexion() as conexion:
            with conexion.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT
                        id_progreso,
                        id_usuario,
                        id_letra,
                        dominada
                    FROM progreso_usuario
                    WHERE id_usuario = %s
                    ORDER BY id_letra;
                    """,
                    (id_usuario,),
                )

                return cursor.fetchall()

    def comprobar_consulta(self, id_usuario):
        respuesta = self.cliente.get(
            "/progreso/letras",
            headers=self.cabeceras_usuario(id_usuario),
        )

        self.assertEqual(
            respuesta.status_code,
            200,
            respuesta.text,
        )

        registros = self.leer_progreso_sql(id_usuario)
        estados_guardados = {
            registro["id_letra"]: registro["dominada"]
            for registro in registros
        }

        # Construye lo esperado desde los datos leídos directamente.
        letras_esperadas = [
            {
                **letra,
                "estado": (
                    "aprendida"
                    if estados_guardados.get(letra["id_letra"], False)
                    else "pendiente"
                ),
            }
            for letra in self.letras
        ]

        self.assertEqual(
            respuesta.json(),
            {
                "total": len(self.letras),
                "letras": letras_esperadas,
            },
        )

        return respuesta.json()

    def test_usuario_sin_progreso_consulta_letras_pendientes(self):
        self.assertEqual(
            self.leer_progreso_sql(self.id_usuario),
            [],
        )

        cuerpo = self.comprobar_consulta(self.id_usuario)

        self.assertTrue(
            all(
                letra["estado"] == "pendiente"
                for letra in cuerpo["letras"]
            )
        )

        # Consultar no debe crear registros de progreso.
        self.assertEqual(
            self.leer_progreso_sql(self.id_usuario),
            [],
        )

    def test_consulta_refleja_registro_y_actualizacion(self):
        self.comprobar_consulta(self.id_usuario)

        respuesta = self.cliente.post(
            "/progreso",
            headers=self.cabeceras_usuario(self.id_usuario),
            json={"id_letra": self.id_letra},
        )

        self.assertEqual(
            respuesta.status_code,
            200,
            respuesta.text,
        )

        registrado = respuesta.json()["progreso"]

        self.assertEqual(
            registrado["id_usuario"],
            self.id_usuario,
        )
        self.assertEqual(
            registrado["id_letra"],
            self.id_letra,
        )
        self.assertIs(registrado["dominada"], True)

        self.assertEqual(
            self.leer_progreso_sql(self.id_usuario),
            [
                {
                    "id_progreso": registrado["id_progreso"],
                    "id_usuario": self.id_usuario,
                    "id_letra": self.id_letra,
                    "dominada": True,
                }
            ],
        )

        self.comprobar_consulta(self.id_usuario)

        for dominada in (False, True):
            with self.subTest(dominada=dominada):
                respuesta = self.cliente.patch(
                    f"/progreso/{self.id_letra}",
                    headers=self.cabeceras_usuario(self.id_usuario),
                    json={"dominada": dominada},
                )

                self.assertEqual(
                    respuesta.status_code,
                    200,
                    respuesta.text,
                )

                actualizado = respuesta.json()["progreso"]

                self.assertEqual(
                    actualizado["id_progreso"],
                    registrado["id_progreso"],
                )
                self.assertEqual(
                    actualizado["id_usuario"],
                    self.id_usuario,
                )
                self.assertEqual(
                    actualizado["id_letra"],
                    self.id_letra,
                )
                self.assertIs(
                    actualizado["dominada"],
                    dominada,
                )

                self.assertEqual(
                    self.leer_progreso_sql(self.id_usuario),
                    [
                        {
                            "id_progreso": registrado["id_progreso"],
                            "id_usuario": self.id_usuario,
                            "id_letra": self.id_letra,
                            "dominada": dominada,
                        }
                    ],
                )

                self.comprobar_consulta(self.id_usuario)


if __name__ == "__main__":
    unittest.main()