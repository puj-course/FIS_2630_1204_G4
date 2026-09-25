import os
import unittest
from uuid import uuid4

from psycopg.rows import dict_row

from app.services.sesiones_service import (
    SesionNoEncontradaError,
    UsuarioNoEncontradoError,
    consultar_sesion,
    consultar_sesiones_usuario,
    crear_sesion,
    finalizar_sesion,
)
from conf.database import obtener_conexion


@unittest.skipUnless(
    os.getenv("DATABASE_URL"),
    "Se necesita DATABASE_URL para probar PostgreSQL",
)
class TestSesionesIntegracion(unittest.TestCase):
    def setUp(self):
        self.usuarios = []
        self.addCleanup(self.eliminar_datos_prueba)

        self.id_usuario = self.crear_usuario_prueba()
        self.id_otro_usuario = self.crear_usuario_prueba()

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
                        "Prueba de sesiones",
                        f"sesiones-{uuid4().hex}@signia.local",
                        "hash-solo-para-pruebas",
                    ),
                )
                id_usuario = cursor.fetchone()["id_usuario"]

        self.usuarios.append(id_usuario)
        return id_usuario

    def eliminar_datos_prueba(self):
        if not self.usuarios:
            return

        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM usuarios
                    WHERE id_usuario = ANY(%s);
                    """,
                    (self.usuarios,),
                )

    def leer_sesion_en_postgresql(self, id_sesion):
        with obtener_conexion() as conexion:
            with conexion.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT
                        id_sesion,
                        id_usuario,
                        fecha_inicio,
                        fecha_fin,
                        estado
                    FROM sesiones_reconocimiento
                    WHERE id_sesion = %s;
                    """,
                    (id_sesion,),
                )
                return cursor.fetchone()

    def test_creacion_persiste_en_otra_conexion(self):
        creada = crear_sesion(self.id_usuario)

        almacenada = self.leer_sesion_en_postgresql(
            creada["id_sesion"]
        )

        self.assertEqual(almacenada, creada)
        self.assertEqual(almacenada["id_usuario"], self.id_usuario)
        self.assertEqual(almacenada["estado"], "activa")
        self.assertIsNone(almacenada["fecha_fin"])
        self.assertIsNotNone(almacenada["fecha_inicio"])
        self.assertIsNotNone(
            almacenada["fecha_inicio"].utcoffset()
        )

        consultada = consultar_sesion(
            self.id_usuario,
            creada["id_sesion"],
        )
        self.assertEqual(consultada, almacenada)

    def test_finalizacion_persiste_y_conserva_fecha_al_repetirse(self):
        creada = crear_sesion(self.id_usuario)

        finalizada = finalizar_sesion(
            self.id_usuario,
            creada["id_sesion"],
        )

        almacenada = self.leer_sesion_en_postgresql(
            creada["id_sesion"]
        )

        self.assertEqual(almacenada, finalizada)
        self.assertEqual(almacenada["estado"], "finalizada")
        self.assertEqual(
            almacenada["fecha_inicio"],
            creada["fecha_inicio"],
        )
        self.assertIsNotNone(almacenada["fecha_fin"])
        self.assertGreaterEqual(
            almacenada["fecha_fin"],
            almacenada["fecha_inicio"],
        )

        repetida = finalizar_sesion(
            self.id_usuario,
            creada["id_sesion"],
        )

        self.assertEqual(repetida, finalizada)
        self.assertEqual(
            self.leer_sesion_en_postgresql(creada["id_sesion"]),
            finalizada,
        )

    def test_sesiones_de_usuarios_permanecen_independientes(self):
        propia = crear_sesion(self.id_usuario)
        ajena = crear_sesion(self.id_otro_usuario)

        with self.assertRaises(SesionNoEncontradaError):
            consultar_sesion(
                self.id_usuario,
                ajena["id_sesion"],
            )

        with self.assertRaises(SesionNoEncontradaError):
            finalizar_sesion(
                self.id_usuario,
                ajena["id_sesion"],
            )

        finalizar_sesion(
            self.id_usuario,
            propia["id_sesion"],
        )

        self.assertEqual(
            self.leer_sesion_en_postgresql(ajena["id_sesion"]),
            ajena,
        )
        self.assertEqual(
            consultar_sesion(
                self.id_otro_usuario,
                ajena["id_sesion"],
            ),
            ajena,
        )

    def test_rechaza_usuario_que_ya_no_existe(self):
        # Elimina exclusivamente un usuario creado por esta prueba.
        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM usuarios WHERE id_usuario = %s;",
                    (self.id_otro_usuario,),
                )

        with self.assertRaises(UsuarioNoEncontradoError):
            crear_sesion(self.id_otro_usuario)

        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM sesiones_reconocimiento
                    WHERE id_usuario = %s;
                    """,
                    (self.id_otro_usuario,),
                )
                self.assertEqual(cursor.fetchone()[0], 0)

    def test_consulta_sesiones_usuario_retorna_solo_sus_sesiones(self):
        propia_1 = crear_sesion(self.id_usuario)
        propia_2 = crear_sesion(self.id_usuario)

        ajena = crear_sesion(self.id_otro_usuario)

        sesiones = consultar_sesiones_usuario(
            self.id_usuario
        )

        ids = [
            sesion["id_sesion"]
            for sesion in sesiones
        ]

        self.assertIn(
            propia_1["id_sesion"],
            ids,
        )

        self.assertIn(
            propia_2["id_sesion"],
            ids,
        )

        self.assertNotIn(
            ajena["id_sesion"],
            ids,
        )


    def test_sesion_mantiene_integridad_con_resultados(self):
        sesion = crear_sesion(
            self.id_usuario
        )

        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM resultados_reconocimiento
                    WHERE id_sesion = %s;
                    """,
                    (sesion["id_sesion"],),
                )

                cantidad = cursor.fetchone()[0]

        self.assertEqual(
            cantidad,
            0,
        )
if __name__ == "__main__":
    unittest.main()