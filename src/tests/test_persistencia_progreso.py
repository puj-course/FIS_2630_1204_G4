import os
import unittest
from uuid import uuid4

from psycopg.rows import dict_row

from app.services.progreso_service import (
    actualizar_estado_progreso,
    consultar_progreso_usuario,
    registrar_progreso,
)
from conf.database import obtener_conexion


@unittest.skipUnless(
    os.getenv("DATABASE_URL"),
    "Se necesita DATABASE_URL para probar PostgreSQL",
)
class TestPersistenciaProgreso(unittest.TestCase):

    def setUp(self):
        self.usuarios_creados = []
        self.addCleanup(self.eliminar_datos_prueba)

        with obtener_conexion() as conexion:
            with conexion.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT id_letra, letra
                    FROM letras
                    WHERE activa = TRUE
                    ORDER BY id_letra
                    LIMIT 1;
                    """
                )
                self.letra = cursor.fetchone()

        if self.letra is None:
            self.skipTest(
                "Se necesita una letra activa para las pruebas"
            )

        self.id_usuario = self.crear_usuario_prueba()

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
                        "Prueba persistencia progreso",
                        f"persistencia-{uuid4().hex}@signia.local",
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

    def leer_desde_otra_conexion(self, id_usuario):
        with obtener_conexion() as conexion:
            with conexion.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT
                        id_progreso,
                        id_usuario,
                        id_letra,
                        cantidad_intentos,
                        cantidad_aciertos,
                        dominada,
                        fecha_ultima_practica,
                        fecha_actualizacion
                    FROM progreso_usuario
                    WHERE id_usuario = %s
                        AND id_letra = %s;
                    """,
                    (id_usuario, self.letra["id_letra"]),
                )

                return cursor.fetchall()

    def test_registro_persiste_despues_de_cerrar_conexion(self):
        registrado = registrar_progreso(
            id_usuario=self.id_usuario,
            id_letra=self.letra["id_letra"],
        )

        # Comprueba los datos desde una conexión nueva.
        almacenados = self.leer_desde_otra_conexion(
            self.id_usuario
        )

        self.assertEqual(almacenados, [registrado])
        self.assertTrue(almacenados[0]["dominada"])

        # Comprueba también la consulta posterior del servicio.
        consultados = consultar_progreso_usuario(
            self.id_usuario
        )

        self.assertEqual(
            consultados,
            [
                {
                    **registrado,
                    "letra": self.letra["letra"],
                }
            ],
        )

    def test_actualizacion_persiste_despues_de_cerrar_conexion(self):
        registrado = registrar_progreso(
            id_usuario=self.id_usuario,
            id_letra=self.letra["id_letra"],
        )

        for dominada in (False, True):
            with self.subTest(dominada=dominada):
                actualizado = actualizar_estado_progreso(
                    id_usuario=self.id_usuario,
                    id_letra=self.letra["id_letra"],
                    dominada=dominada,
                )

                almacenados = self.leer_desde_otra_conexion(
                    self.id_usuario
                )

                self.assertEqual(almacenados, [actualizado])
                self.assertEqual(
                    actualizado["id_progreso"],
                    registrado["id_progreso"],
                )
                self.assertEqual(
                    actualizado["dominada"],
                    dominada,
                )

                # Cambiar el estado conserva los datos de práctica.
                for campo in (
                    "cantidad_intentos",
                    "cantidad_aciertos",
                    "fecha_ultima_practica",
                ):
                    self.assertEqual(
                        actualizado[campo],
                        registrado[campo],
                    )

                consultados = consultar_progreso_usuario(
                    self.id_usuario
                )

                self.assertEqual(
                    consultados,
                    [
                        {
                            **actualizado,
                            "letra": self.letra["letra"],
                        }
                    ],
                )

    def test_registrar_repetidamente_no_crea_duplicados(self):
        primero = registrar_progreso(
            id_usuario=self.id_usuario,
            id_letra=self.letra["id_letra"],
        )

        for repeticion in range(3):
            with self.subTest(repeticion=repeticion):
                repetido = registrar_progreso(
                    id_usuario=self.id_usuario,
                    id_letra=self.letra["id_letra"],
                )

                self.assertEqual(
                    repetido["id_progreso"],
                    primero["id_progreso"],
                )

                almacenados = self.leer_desde_otra_conexion(
                    self.id_usuario
                )

                # Debe existir exactamente el mismo registro.
                self.assertEqual(almacenados, [repetido])
                self.assertTrue(almacenados[0]["dominada"])

    def test_progresos_de_usuarios_permanecen_independientes(self):
        otro_usuario = self.crear_usuario_prueba()

        progreso_1 = registrar_progreso(
            id_usuario=self.id_usuario,
            id_letra=self.letra["id_letra"],
        )
        progreso_2 = registrar_progreso(
            id_usuario=otro_usuario,
            id_letra=self.letra["id_letra"],
        )

        self.assertNotEqual(
            progreso_1["id_progreso"],
            progreso_2["id_progreso"],
        )

        # Modifica únicamente el progreso del primer usuario.
        actualizado = actualizar_estado_progreso(
            id_usuario=self.id_usuario,
            id_letra=self.letra["id_letra"],
            dominada=False,
        )

        almacenados_1 = self.leer_desde_otra_conexion(
            self.id_usuario
        )
        almacenados_2 = self.leer_desde_otra_conexion(
            otro_usuario
        )

        self.assertEqual(almacenados_1, [actualizado])
        self.assertEqual(almacenados_2, [progreso_2])
        self.assertFalse(almacenados_1[0]["dominada"])
        self.assertTrue(almacenados_2[0]["dominada"])

        # Cada consulta devuelve únicamente el progreso propio.
        self.assertEqual(
            consultar_progreso_usuario(self.id_usuario),
            [
                {
                    **actualizado,
                    "letra": self.letra["letra"],
                }
            ],
        )
        self.assertEqual(
            consultar_progreso_usuario(otro_usuario),
            [
                {
                    **progreso_2,
                    "letra": self.letra["letra"],
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()