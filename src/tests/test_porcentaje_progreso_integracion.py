"""Valida el porcentaje de avance con SQL real en PostgreSQL (issue #363).

Usa DATABASE_URL y copias temporales vacías de las tablas existentes.
Los servicios conservan sus consultas reales; solo se dirige su conexión
a la sesión que contiene las tablas temporales. No modifica datos públicos.
"""

import os
import unittest
from contextlib import contextmanager
from unittest.mock import patch

from psycopg import sql
from psycopg.rows import dict_row

from app.services.perfil_service import obtener_progreso_usuario
from app.services.progreso_service import (
    actualizar_estado_progreso,
    registrar_progreso,
)
from conf.database import obtener_conexion
from src.schemas.perfil import ProgresoPerfilRespuesta


@unittest.skipUnless(
    os.getenv("DATABASE_URL"),
    "Se necesita DATABASE_URL para probar PostgreSQL",
)
class TestPorcentajeProgresoIntegracion(unittest.TestCase):
    def setUp(self):
        self.conexion = obtener_conexion()
        self.addCleanup(self.conexion.close)
        self.conexion.autocommit = True
        # Mantiene una única transacción incluso con conexiones de un pool.
        # Al finalizar revierte también la creación de las tablas temporales.
        transaccion = self.conexion.transaction(force_rollback=True)
        transaccion.__enter__()
        self.addCleanup(transaccion.__exit__, None, None, None)

        with self.conexion.transaction():
            with self.conexion.cursor(row_factory=dict_row) as cursor:
                for tabla in ("usuarios", "letras", "progreso_usuario"):
                    # INCLUDING ALL copia columnas, identidad e índices.
                    # Cada identidad temporal tiene su propia secuencia.
                    cursor.execute(
                        sql.SQL(
                            "CREATE TEMP TABLE {} "
                            "(LIKE {} INCLUDING ALL) "
                            "ON COMMIT PRESERVE ROWS"
                        ).format(
                            sql.Identifier(tabla),
                            sql.Identifier("public", tabla),
                        )
                    )

                self.usuarios = []
                for numero in (1, 2):
                    cursor.execute(
                        """
                        INSERT INTO pg_temp.usuarios (
                            nombre, correo, contrasena_hash
                        )
                        VALUES (%s, %s, %s)
                        RETURNING id_usuario;
                        """,
                        (
                            f"Prueba porcentaje {numero}",
                            f"porcentaje-{numero}@signia.local",
                            "hash-solo-para-pruebas",
                        ),
                    )
                    self.usuarios.append(cursor.fetchone()["id_usuario"])

                self.letras = {}
                for letra, activa in (
                    ("A", True),
                    ("B", True),
                    ("C", True),
                    ("Z", False),
                ):
                    cursor.execute(
                        """
                        INSERT INTO pg_temp.letras (letra, activa)
                        VALUES (%s, %s)
                        RETURNING id_letra;
                        """,
                        (letra, activa),
                    )
                    self.letras[letra] = cursor.fetchone()["id_letra"]

        for modulo in ("perfil_service", "progreso_service"):
            parche = patch(
                f"app.services.{modulo}.obtener_conexion",
                side_effect=self.conexion_temporal,
            )
            parche.start()
            self.addCleanup(parche.stop)

    @contextmanager
    def conexion_temporal(self):
        # Cada servicio usa un savepoint real dentro de la transacción de prueba.
        # El contexto no cierra la conexión que contiene las tablas temporales.
        with self.conexion.transaction():
            yield self.conexion

    def comprobar_porcentaje(self, usuario, aprendidas, esperado, total=3):
        progreso = obtener_progreso_usuario(usuario)
        self.assertEqual(progreso["total_letras"], total)
        self.assertEqual(progreso["letras_dominadas"], aprendidas)
        self.assertEqual(progreso["porcentaje_progreso"], esperado)
        self.assertGreaterEqual(progreso["porcentaje_progreso"], 0)
        self.assertLessEqual(progreso["porcentaje_progreso"], 100)
        ProgresoPerfilRespuesta(**progreso)
        return progreso

    def test_usuario_sin_progreso_tiene_cero_por_ciento(self):
        progreso = self.comprobar_porcentaje(self.usuarios[0], 0, 0.0)
        self.assertEqual(progreso["letras_iniciadas"], 0)
        self.assertEqual(progreso["cantidad_intentos"], 0)
        self.assertEqual(progreso["cantidad_aciertos"], 0)

    def test_avance_parcial_y_completo_se_calculan_desde_datos_guardados(self):
        usuario = self.usuarios[0]
        for letra, aprendidas, porcentaje in (
            ("A", 1, 33.33),
            ("B", 2, 66.67),
            ("C", 3, 100.0),
        ):
            with self.subTest(letra=letra, porcentaje=porcentaje):
                registrar_progreso(usuario, self.letras[letra])
                self.comprobar_porcentaje(usuario, aprendidas, porcentaje)

    def test_letra_practicada_no_dominada_no_cuenta_como_aprendida(self):
        usuario = self.usuarios[0]
        with self.conexion.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO pg_temp.progreso_usuario (
                    id_usuario, id_letra, cantidad_intentos,
                    cantidad_aciertos, dominada
                )
                VALUES (%s, %s, 5, 2, FALSE);
                """,
                (usuario, self.letras["A"]),
            )

        progreso = self.comprobar_porcentaje(usuario, 0, 0.0)
        self.assertEqual(progreso["letras_iniciadas"], 1)
        self.assertEqual(progreso["cantidad_intentos"], 5)
        self.assertEqual(progreso["cantidad_aciertos"], 2)

    def test_letra_inactiva_no_se_incluye_en_ninguno_de_los_conteos(self):
        usuario = self.usuarios[0]
        registrar_progreso(usuario, self.letras["Z"])
        self.comprobar_porcentaje(usuario, 0, 0.0)

        registrar_progreso(usuario, self.letras["A"])
        self.comprobar_porcentaje(usuario, 1, 33.33)

    def test_letras_repetidas_no_aumentan_el_porcentaje(self):
        usuario = self.usuarios[0]
        primero = registrar_progreso(usuario, self.letras["A"])
        for _ in range(3):
            repetido = registrar_progreso(usuario, self.letras["A"])
            self.assertEqual(repetido["id_progreso"], primero["id_progreso"])

        self.comprobar_porcentaje(usuario, 1, 33.33)
        with self.conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*) FROM pg_temp.progreso_usuario
                WHERE id_usuario = %s AND id_letra = %s;
                """,
                (usuario, self.letras["A"]),
            )
            self.assertEqual(cursor.fetchone()[0], 1)

    def test_cada_usuario_tiene_su_propio_porcentaje(self):
        primero, segundo = self.usuarios
        registrar_progreso(primero, self.letras["A"])
        self.comprobar_porcentaje(segundo, 0, 0.0)

        registrar_progreso(segundo, self.letras["B"])
        registrar_progreso(segundo, self.letras["C"])
        self.comprobar_porcentaje(primero, 1, 33.33)
        self.comprobar_porcentaje(segundo, 2, 66.67)

    def test_catalogo_sin_letras_activas_devuelve_cero(self):
        usuario = self.usuarios[0]
        registrar_progreso(usuario, self.letras["A"])
        with self.conexion.cursor() as cursor:
            cursor.execute("UPDATE pg_temp.letras SET activa = FALSE;")

        progreso = self.comprobar_porcentaje(usuario, 0, 0.0, total=0)
        self.assertEqual(progreso["cantidad_intentos"], 0)
        self.assertEqual(progreso["cantidad_aciertos"], 0)

    def test_porcentaje_refleja_cambios_del_estado_almacenado(self):
        usuario = self.usuarios[0]
        registrar_progreso(usuario, self.letras["A"])
        self.comprobar_porcentaje(usuario, 1, 33.33)

        actualizar_estado_progreso(usuario, self.letras["A"], False)
        self.comprobar_porcentaje(usuario, 0, 0.0)


if __name__ == "__main__":
    unittest.main()
