import os
import unittest
from contextlib import contextmanager
from unittest.mock import patch
from uuid import uuid4

from psycopg.rows import dict_row

from app.services.progreso_service import (
    actualizar_estado_progreso,
    consultar_estado_letras_usuario,
    registrar_progreso,
)
from conf.database import obtener_conexion
from src.schemas.progreso import ConsultaEstadoLetrasRespuesta


@unittest.skipUnless(
    os.getenv("DATABASE_URL"),
    "Se necesita DATABASE_URL para probar PostgreSQL",
)
class TestEstadoLetrasIntegracion(unittest.TestCase):

    def setUp(self):
        self.conexion = obtener_conexion()
        self.addCleanup(self.conexion.close)
        self.addCleanup(self.conexion.rollback)

        with self.conexion.cursor(
            row_factory=dict_row
        ) as cursor:
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

        if len(self.letras) < 3:
            self.skipTest(
                "Se necesitan al menos tres letras activas"
            )

        self.usuario_1 = self.crear_usuario()
        self.usuario_2 = self.crear_usuario()

        # Los servicios ejecutan su SQL real en la transacción
        # de prueba, que se revierte al finalizar.
        reemplazo = patch(
            "app.services.progreso_service.obtener_conexion",
            side_effect=self.conexion_de_prueba,
        )
        reemplazo.start()
        self.addCleanup(reemplazo.stop)

    @contextmanager
    def conexion_de_prueba(self):
        with self.conexion.transaction():
            yield self.conexion

    def crear_usuario(self):
        with self.conexion.cursor(
            row_factory=dict_row
        ) as cursor:
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
                    "Prueba estado de letras",
                    f"estado-{uuid4().hex}@signia.local",
                    "hash-solo-para-pruebas",
                ),
            )

            return cursor.fetchone()["id_usuario"]

    def consultar_y_validar(self, id_usuario):
        letras = consultar_estado_letras_usuario(
            id_usuario=id_usuario,
        )

        respuesta = ConsultaEstadoLetrasRespuesta(
            total=len(letras),
            letras=letras,
        )

        self.assertEqual(
            respuesta.total,
            len(self.letras),
        )

        # Comprueba que estén todas las letras activas,
        # sin duplicados y con el orden esperado.
        self.assertEqual(
            [letra["id_letra"] for letra in letras],
            [letra["id_letra"] for letra in self.letras],
        )

        return letras

    def test_sin_progreso_todas_las_letras_estan_pendientes(self):
        # Otro usuario ya aprendió una letra.
        registrar_progreso(
            id_usuario=self.usuario_2,
            id_letra=self.letras[0]["id_letra"],
        )

        letras = self.consultar_y_validar(self.usuario_1)

        # El usuario sin progreso debe ver todas pendientes.
        self.assertEqual(
            letras,
            [
                {
                    **letra,
                    "estado": "pendiente",
                }
                for letra in self.letras
            ],
        )

    def test_estados_independientes_y_actualizados(self):
        primera = self.letras[0]["id_letra"]
        segunda = self.letras[1]["id_letra"]
        tercera = self.letras[2]["id_letra"]

        registrar_progreso(
            id_usuario=self.usuario_1,
            id_letra=primera,
        )

        registrar_progreso(
            id_usuario=self.usuario_1,
            id_letra=segunda,
        )
        actualizar_estado_progreso(
            id_usuario=self.usuario_1,
            id_letra=segunda,
            dominada=False,
        )

        registrar_progreso(
            id_usuario=self.usuario_2,
            id_letra=segunda,
        )

        letras_1 = self.consultar_y_validar(self.usuario_1)
        letras_2 = self.consultar_y_validar(self.usuario_2)

        estados_1 = {
            letra["id_letra"]: letra["estado"]
            for letra in letras_1
        }
        estados_2 = {
            letra["id_letra"]: letra["estado"]
            for letra in letras_2
        }

        self.assertEqual(estados_1[primera], "aprendida")
        self.assertEqual(estados_1[segunda], "pendiente")
        self.assertEqual(estados_1[tercera], "pendiente")

        self.assertEqual(estados_2[primera], "pendiente")
        self.assertEqual(estados_2[segunda], "aprendida")
        self.assertEqual(estados_2[tercera], "pendiente")

        # Cambia el estado y vuelve a consultar.
        actualizar_estado_progreso(
            id_usuario=self.usuario_1,
            id_letra=primera,
            dominada=False,
        )

        letras_actualizadas = self.consultar_y_validar(
            self.usuario_1
        )

        self.assertEqual(
            letras_actualizadas,
            [
                {
                    **letra,
                    "estado": "pendiente",
                }
                for letra in self.letras
            ],
        )

        # El segundo usuario conserva exactamente su progreso.
        self.assertEqual(
            self.consultar_y_validar(self.usuario_2),
            letras_2,
        )


if __name__ == "__main__":
    unittest.main()