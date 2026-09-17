import os
import unittest
from contextlib import contextmanager
from unittest.mock import patch
from uuid import uuid4

from psycopg.rows import dict_row

from app.services.progreso_service import consultar_progreso_usuario
from conf.database import obtener_conexion
from src.schemas.progreso import ConsultaProgresoRespuesta


@unittest.skipUnless(
    os.getenv("DATABASE_URL"),
    "Se necesita DATABASE_URL para probar PostgreSQL",
)
class TestConsultaProgresoIntegracion(unittest.TestCase):

    def setUp(self):
        self.conexion = obtener_conexion()
        self.addCleanup(self.conexion.close)
        self.addCleanup(self.conexion.rollback)

        self.conexion.autocommit = False

        with self.conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT id_letra, letra
                FROM letras
                ORDER BY letra, id_letra
                LIMIT 2;
                """
            )
            self.letras = cursor.fetchall()

            if len(self.letras) < 2:
                self.skipTest(
                    "Se necesitan dos letras registradas"
                )

            self.usuarios = []

            for numero in range(3):
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
                        f"Prueba consulta progreso {numero}",
                        f"consulta-{uuid4().hex}@signia.local",
                        "hash-solo-para-pruebas",
                    ),
                )

                self.usuarios.append(
                    cursor.fetchone()["id_usuario"]
                )

        conexion_simulada = patch(
            "app.services.progreso_service.obtener_conexion",
            side_effect=self.usar_conexion_prueba,
        )
        conexion_simulada.start()
        self.addCleanup(conexion_simulada.stop)

    @contextmanager
    def usar_conexion_prueba(self):
        # Mantiene las operaciones dentro de la transacción de prueba
        with self.conexion.transaction():
            yield self.conexion

    def crear_progreso(self, id_usuario, letra, dominada):
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
                VALUES (%s, %s, 3, 2, %s, CURRENT_TIMESTAMP)
                RETURNING
                    id_progreso,
                    id_usuario,
                    id_letra,
                    cantidad_intentos,
                    cantidad_aciertos,
                    dominada,
                    fecha_ultima_practica,
                    fecha_actualizacion;
                """,
                (
                    id_usuario,
                    letra["id_letra"],
                    dominada,
                ),
            )

            progreso = cursor.fetchone()

        return {
            **progreso,
            "letra": letra["letra"],
        }

    def test_consulta_separa_usuarios_y_recupera_estados(self):
        usuario_1, usuario_2, _ = self.usuarios
        letra_1, letra_2 = self.letras

        # Inserta en orden inverso para comprobar el orden de consulta
        progreso_2 = self.crear_progreso(
            usuario_1,
            letra_2,
            False,
        )
        progreso_1 = self.crear_progreso(
            usuario_1,
            letra_1,
            True,
        )

        # La misma letra tiene un estado diferente para otro usuario
        progreso_otro_usuario = self.crear_progreso(
            usuario_2,
            letra_1,
            False,
        )

        resultados_1 = consultar_progreso_usuario(usuario_1)
        resultados_2 = consultar_progreso_usuario(usuario_2)

        self.assertEqual(
            resultados_1,
            [progreso_1, progreso_2],
        )
        self.assertEqual(
            resultados_2,
            [progreso_otro_usuario],
        )

        # Comprueba que los datos reales cumplen el esquema de salida
        respuesta = ConsultaProgresoRespuesta(
            total=len(resultados_1),
            progresos=resultados_1,
        )

        self.assertEqual(respuesta.total, 2)
        self.assertTrue(respuesta.progresos[0].dominada)
        self.assertFalse(respuesta.progresos[1].dominada)

    def test_usuario_sin_progreso_recibe_lista_vacia(self):
        usuario_1, _, usuario_sin_progreso = self.usuarios

        # Hay datos en la tabla, pero pertenecen a otro usuario
        self.crear_progreso(
            usuario_1,
            self.letras[0],
            True,
        )

        resultados = consultar_progreso_usuario(
            usuario_sin_progreso
        )

        self.assertEqual(resultados, [])

        respuesta = ConsultaProgresoRespuesta(
            total=len(resultados),
            progresos=resultados,
        )

        self.assertEqual(
            respuesta.model_dump(),
            {
                "total": 0,
                "progresos": [],
            },
        )


if __name__ == "__main__":
    unittest.main()