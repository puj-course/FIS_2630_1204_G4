import os
import unittest
from contextlib import contextmanager
from datetime import datetime, timezone
from unittest.mock import patch
from uuid import uuid4

from psycopg.rows import dict_row

from app.services.progreso_service import registrar_progreso
from conf.database import obtener_conexion


@unittest.skipUnless(
    os.getenv("DATABASE_URL"),
    "La prueba requiere DATABASE_URL",
)
class TestIntegracionProgreso(unittest.TestCase):

    def setUp(self):
        self.conexion = obtener_conexion()

        # Registra la limpieza incluso si falla la preparación
        self.addCleanup(self.conexion.close)
        self.addCleanup(self.conexion.rollback)

        self.conexion.autocommit = False

        with self.conexion.cursor(row_factory=dict_row) as cursor:
            # Utiliza una letra existente sin modificarla
            cursor.execute(
                """
                SELECT id_letra
                FROM letras
                WHERE activa = TRUE
                ORDER BY id_letra
                LIMIT 1;
                """
            )

            letra = cursor.fetchone()

            if letra is None:
                self.skipTest(
                    "La prueba requiere una letra activa"
                )

            self.id_letra = letra["id_letra"]

            # Crea un usuario temporal
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
                    "Usuario prueba progreso",
                    f"progreso-{uuid4().hex}@signia.local",
                    "hash-solo-para-pruebas",
                ),
            )

            self.id_usuario = cursor.fetchone()["id_usuario"]

        parche = patch(
            "app.services.progreso_service.obtener_conexion",
            side_effect=self.usar_conexion_prueba,
        )

        parche.start()
        self.addCleanup(parche.stop)

    @contextmanager
    def usar_conexion_prueba(self):
        # Mantiene las operaciones dentro de la transacción de prueba
        with self.conexion.transaction():
            yield self.conexion

    def consultar_progreso(self):
        with self.conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    id_progreso,
                    id_usuario,
                    id_letra,
                    cantidad_intentos,
                    cantidad_aciertos,
                    dominada,
                    fecha_ultima_practica
                FROM progreso_usuario
                WHERE id_usuario = %s
                    AND id_letra = %s;
                """,
                (self.id_usuario, self.id_letra),
            )

            return cursor.fetchall()

    def test_registro_repetido_no_crea_duplicados(self):
        primero = registrar_progreso(
            self.id_usuario,
            self.id_letra,
        )

        segundo = registrar_progreso(
            self.id_usuario,
            self.id_letra,
        )

        self.assertEqual(
            primero["id_progreso"],
            segundo["id_progreso"],
        )

        filas = self.consultar_progreso()

        self.assertEqual(len(filas), 1)

        progreso = filas[0]

        self.assertEqual(
            progreso["id_progreso"],
            primero["id_progreso"],
        )
        self.assertEqual(
            progreso["id_usuario"],
            self.id_usuario,
        )
        self.assertEqual(
            progreso["id_letra"],
            self.id_letra,
        )
        self.assertTrue(progreso["dominada"])
        self.assertEqual(progreso["cantidad_intentos"], 0)
        self.assertEqual(progreso["cantidad_aciertos"], 0)
        self.assertIsNone(progreso["fecha_ultima_practica"])

    def test_conserva_contadores_del_progreso_existente(self):
        fecha_practica = datetime(
            2026, 9, 1, tzinfo=timezone.utc
        )

        with self.conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                INSERT INTO progreso_usuario (
                    id_usuario,
                    id_letra,
                    cantidad_intentos,
                    cantidad_aciertos,
                    dominada,
                    fecha_ultima_practica
                )
                VALUES (%s, %s, 7, 5, FALSE, %s)
                RETURNING id_progreso;
                """,
                (
                    self.id_usuario,
                    self.id_letra,
                    fecha_practica,
                ),
            )

            id_original = cursor.fetchone()["id_progreso"]

        resultado = registrar_progreso(
            self.id_usuario,
            self.id_letra,
        )

        self.assertEqual(
            resultado["id_progreso"],
            id_original,
        )

        filas = self.consultar_progreso()

        self.assertEqual(len(filas), 1)

        progreso = filas[0]

        self.assertEqual(progreso["id_progreso"], id_original)
        self.assertTrue(progreso["dominada"])
        self.assertEqual(progreso["cantidad_intentos"], 7)
        self.assertEqual(progreso["cantidad_aciertos"], 5)
        self.assertEqual(
            progreso["fecha_ultima_practica"],
            fecha_practica,
        )


if __name__ == "__main__":
    unittest.main()