import os
import unittest
from contextlib import contextmanager
from unittest.mock import patch
from uuid import uuid4

from psycopg.rows import dict_row

from app.services.progreso_service import (
    ProgresoNoEncontradoError,
    actualizar_estado_progreso,
)
from conf.database import obtener_conexion


@unittest.skipUnless(
    os.getenv("DATABASE_URL"),
    "La prueba requiere DATABASE_URL",
)
class TestActualizarEstadoProgresoIntegracion(unittest.TestCase):

    def setUp(self):
        self.conexion = obtener_conexion()

        self.addCleanup(self.conexion.close)
        self.addCleanup(self.conexion.rollback)

        self.conexion.autocommit = False

        with self.conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT id_letra
                FROM letras
                WHERE activa = TRUE
                ORDER BY id_letra
                LIMIT 2;
                """
            )

            letras = cursor.fetchall()

            if len(letras) < 2:
                self.skipTest(
                    "La prueba requiere dos letras activas"
                )

            self.letra_1 = letras[0]["id_letra"]
            self.letra_2 = letras[1]["id_letra"]

            self.usuarios = []

            for numero in (1, 2):
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
                        f"Usuario prueba estado {numero}",
                        f"estado-{uuid4().hex}@signia.local",
                        "hash-solo-para-pruebas",
                    ),
                )

                self.usuarios.append(
                    cursor.fetchone()["id_usuario"]
                )

        parche = patch(
            "app.services.progreso_service.obtener_conexion",
            side_effect=self.usar_conexion_prueba,
        )

        parche.start()
        self.addCleanup(parche.stop)

    @contextmanager
    def usar_conexion_prueba(self):
        with self.conexion.transaction():
            yield self.conexion

    def crear_progreso(self, id_usuario, id_letra):
        with self.conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                INSERT INTO progreso_usuario (
                    id_usuario,
                    id_letra,
                    cantidad_intentos,
                    cantidad_aciertos,
                    dominada,
                    fecha_ultima_practica,
                    fecha_actualizacion
                )
                VALUES (
                    %s,
                    %s,
                    7,
                    5,
                    FALSE,
                    CURRENT_TIMESTAMP - INTERVAL '2 days',
                    CURRENT_TIMESTAMP - INTERVAL '1 day'
                )
                RETURNING *;
                """,
                (id_usuario, id_letra),
            )

            return cursor.fetchone()

    def consultar_progreso(self, id_usuario, id_letra):
        with self.conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT *
                FROM progreso_usuario
                WHERE id_usuario = %s
                    AND id_letra = %s;
                """,
                (id_usuario, id_letra),
            )

            return cursor.fetchone()

    def test_actualiza_estado_fecha_y_conserva_otros_registros(self):
        usuario_1, usuario_2 = self.usuarios

        original = self.crear_progreso(
            usuario_1, self.letra_1
        )
        otra_letra = self.crear_progreso(
            usuario_1, self.letra_2
        )
        otro_usuario = self.crear_progreso(
            usuario_2, self.letra_1
        )

        with self.conexion.cursor() as cursor:
            cursor.execute("SELECT CURRENT_TIMESTAMP;")
            fecha_esperada = cursor.fetchone()[0]

        for estado in (True, False):
            with self.subTest(dominada=estado):
                resultado = actualizar_estado_progreso(
                    usuario_1,
                    self.letra_1,
                    estado,
                )

                almacenado = self.consultar_progreso(
                    usuario_1, self.letra_1
                )

                self.assertEqual(
                    resultado["id_progreso"],
                    original["id_progreso"],
                )
                self.assertEqual(
                    almacenado["id_progreso"],
                    original["id_progreso"],
                )
                self.assertEqual(
                    almacenado["dominada"],
                    estado,
                )
                self.assertEqual(
                    almacenado["fecha_actualizacion"],
                    fecha_esperada,
                )
                self.assertGreater(
                    almacenado["fecha_actualizacion"],
                    original["fecha_actualizacion"],
                )

                for campo in (
                    "id_usuario",
                    "id_letra",
                    "cantidad_intentos",
                    "cantidad_aciertos",
                    "fecha_ultima_practica",
                ):
                    self.assertEqual(
                        almacenado[campo],
                        original[campo],
                    )

                self.assertEqual(
                    self.consultar_progreso(
                        usuario_1, self.letra_2
                    ),
                    otra_letra,
                )
                self.assertEqual(
                    self.consultar_progreso(
                        usuario_2, self.letra_1
                    ),
                    otro_usuario,
                )

    def test_progreso_inexistente_no_crea_registro(self):
        usuario_1, usuario_2 = self.usuarios

        progreso_otro_usuario = self.crear_progreso(
            usuario_2, self.letra_1
        )

        with self.assertRaises(ProgresoNoEncontradoError):
            actualizar_estado_progreso(
                usuario_1,
                self.letra_1,
                True,
            )

        self.assertIsNone(
            self.consultar_progreso(
                usuario_1, self.letra_1
            )
        )
        self.assertEqual(
            self.consultar_progreso(
                usuario_2, self.letra_1
            ),
            progreso_otro_usuario,
        )


if __name__ == "__main__":
    unittest.main()