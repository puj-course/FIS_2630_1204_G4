import os
import unittest
from contextlib import contextmanager
from uuid import uuid4
from unittest.mock import patch

from fastapi.testclient import TestClient
from psycopg.rows import dict_row

from app.main import app
from app.security import obtener_usuario_actual
from conf.database import obtener_conexion


@unittest.skipUnless(
    os.getenv("DATABASE_URL"),
    "La prueba requiere DATABASE_URL",
)
class TestIntegracionResultados(unittest.TestCase):

    def setUp(self):
        self.conexion = obtener_conexion()
        self.conexion.autocommit = False

        with self.conexion.cursor(
            row_factory=dict_row
        ) as cursor:
            cursor.execute(
                """
                SELECT
                    id_letra,
                    letra
                FROM letras
                WHERE letra IN ('A', 'B')
                    AND activa = TRUE;
                """
            )

            letras = {
                registro["letra"]: registro["id_letra"]
                for registro in cursor.fetchall()
            }

            if "A" not in letras or "B" not in letras:
                self.conexion.rollback()
                self.conexion.close()

                self.skipTest(
                    "La prueba requiere las letras A y B activas"
                )

            self.id_letra_a = letras["A"]
            self.id_letra_b = letras["B"]

            correo = (
                f"integracion-{uuid4().hex}@signia.local"
            )

            cursor.execute(
                """
                INSERT INTO usuarios (
                    nombre,
                    correo,
                    contrasena_hash,
                    rol
                )
                VALUES (%s, %s, %s, 'usuario')
                RETURNING
                    id_usuario,
                    nombre,
                    correo,
                    rol;
                """,
                (
                    "Usuario integración",
                    correo,
                    "hash-prueba-integracion",
                )
            )

            self.usuario = cursor.fetchone()

        app.dependency_overrides.clear()
        app.dependency_overrides[
            obtener_usuario_actual
        ] = lambda: self.usuario

        self.cliente = TestClient(app)

        self.parche_conexion = patch(
            "app.services."
            "resultados_reconocimiento_service."
            "obtener_conexion",
            side_effect=self.usar_conexion_prueba,
        )

        self.parche_conexion.start()

    @contextmanager
    def usar_conexion_prueba(self):
        yield self.conexion

    def tearDown(self):
        app.dependency_overrides.clear()
        self.parche_conexion.stop()
        self.cliente.close()

        self.conexion.rollback()
        self.conexion.close()

    def test_registra_y_recupera_multiples_resultados(self):
        primer_resultado = self.cliente.post(
            "/resultados-reconocimiento",
            json={
                "id_letra_objetivo": self.id_letra_a,
                "letra_detectada": "A",
                "confianza": 0.95,
            },
        )

        segundo_resultado = self.cliente.post(
            "/resultados-reconocimiento",
            json={
                "id_letra_objetivo": self.id_letra_a,
                "letra_detectada": "B",
                "confianza": 0.80,
            },
        )

        self.assertEqual(
            primer_resultado.status_code,
            201,
        )
        self.assertEqual(
            segundo_resultado.status_code,
            201,
        )

        consulta = self.cliente.get(
            "/resultados-reconocimiento"
        )

        self.assertEqual(consulta.status_code, 200)
        self.assertEqual(consulta.json()["total"], 2)

        resultados = consulta.json()["resultados"]

        self.assertEqual(len(resultados), 2)

        self.assertTrue(
            all(
                resultado["id_usuario"]
                == self.usuario["id_usuario"]
                for resultado in resultados
            )
        )

        self.assertEqual(
            {
                resultado["letra_detectada"]
                for resultado in resultados
            },
            {"A", "B"},
        )

        self.assertEqual(
            {
                resultado["es_correcto"]
                for resultado in resultados
            },
            {True, False},
        )

        with self.conexion.cursor(
            row_factory=dict_row
        ) as cursor:
            cursor.execute(
                """
                SELECT
                    COUNT(
                        DISTINCT s.id_sesion
                    ) AS total_sesiones,
                    COUNT(
                        r.id_resultado
                    ) AS total_resultados
                FROM sesiones_reconocimiento AS s
                INNER JOIN resultados_reconocimiento AS r
                    ON r.id_sesion = s.id_sesion
                WHERE s.id_usuario = %s;
                """,
                (self.usuario["id_usuario"],)
            )

            registro = cursor.fetchone()

        self.assertEqual(
            registro["total_sesiones"],
            2,
        )
        self.assertEqual(
            registro["total_resultados"],
            2,
        )
    def test_separa_resultados_de_usuarios_diferentes(self):
        primer_registro = self.cliente.post(
            "/resultados-reconocimiento",
            json={
                "id_letra_objetivo": self.id_letra_a,
                "letra_detectada": "A",
                "confianza": 0.92,
            },
        )

        self.assertEqual(
            primer_registro.status_code,
            201,
        )

        with self.conexion.cursor(
            row_factory=dict_row
        ) as cursor:
            correo_segundo = (
                f"integracion-segundo-"
                f"{uuid4().hex}@signia.local"
            )

            cursor.execute(
                """
                INSERT INTO usuarios (
                    nombre,
                    correo,
                    contrasena_hash,
                    rol
                )
                VALUES (%s, %s, %s, 'usuario')
                RETURNING
                    id_usuario,
                    nombre,
                    correo,
                    rol;
                """,
                (
                    "Segundo usuario integración",
                    correo_segundo,
                    "hash-prueba-integracion",
                )
            )

            segundo_usuario = cursor.fetchone()

        app.dependency_overrides[
            obtener_usuario_actual
        ] = lambda: segundo_usuario

        segundo_registro = self.cliente.post(
            "/resultados-reconocimiento",
            json={
                "id_letra_objetivo": self.id_letra_b,
                "letra_detectada": "B",
                "confianza": 0.89,
            },
        )

        self.assertEqual(
            segundo_registro.status_code,
            201,
        )

        consulta_segundo = self.cliente.get(
            "/resultados-reconocimiento"
        )

        self.assertEqual(
            consulta_segundo.status_code,
            200,
        )
        self.assertEqual(
            consulta_segundo.json()["total"],
            1,
        )
        self.assertEqual(
            consulta_segundo.json()["resultados"][0][
                "id_usuario"
            ],
            segundo_usuario["id_usuario"],
        )

        app.dependency_overrides[
            obtener_usuario_actual
        ] = lambda: self.usuario

        consulta_primero = self.cliente.get(
            "/resultados-reconocimiento"
        )

        self.assertEqual(
            consulta_primero.status_code,
            200,
        )
        self.assertEqual(
            consulta_primero.json()["total"],
            1,
        )
        self.assertEqual(
            consulta_primero.json()["resultados"][0][
                "id_usuario"
            ],
            self.usuario["id_usuario"],
        )

        with self.conexion.cursor(
            row_factory=dict_row
        ) as cursor:
            cursor.execute(
                """
                SELECT
                    s.id_usuario,
                    COUNT(r.id_resultado) AS total
                FROM sesiones_reconocimiento AS s
                INNER JOIN resultados_reconocimiento AS r
                    ON r.id_sesion = s.id_sesion
                WHERE s.id_usuario IN (%s, %s)
                GROUP BY s.id_usuario;
                """,
                (
                    self.usuario["id_usuario"],
                    segundo_usuario["id_usuario"],
                )
            )

            cantidades = {
                registro["id_usuario"]: registro["total"]
                for registro in cursor.fetchall()
            }

        self.assertEqual(
            cantidades,
            {
                self.usuario["id_usuario"]: 1,
                segundo_usuario["id_usuario"]: 1,
            },
        )

if __name__ == "__main__":
    unittest.main()