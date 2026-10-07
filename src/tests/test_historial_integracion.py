import os
import unittest
from unittest.mock import patch
from uuid import uuid4

from psycopg.rows import dict_row

from app.services.historial_service import consultar_historial_usuario
from app.services.resultados_service import registrar_resultado
from app.services.sesiones_service import crear_sesion, finalizar_sesion
from conf.database import obtener_conexion


@unittest.skipUnless(
    os.getenv("DATABASE_URL"),
    "Se necesita DATABASE_URL para probar PostgreSQL",
)
class TestHistorialIntegracion(unittest.TestCase):
    def setUp(self):
        self.usuarios = []
        self.addCleanup(self.eliminar_datos_prueba)

        parche = patch.dict(
            os.environ,
            {"APRENDIZAJE_MIN_ACIERTOS": "3"},
        )
        parche.start()
        self.addCleanup(parche.stop)

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
                        "Prueba integración historial",
                        f"historial-{uuid4().hex}@signia.local",
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

    def obtener_letras_prueba(self):
        with obtener_conexion() as conexion:
            with conexion.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT id_letra, letra
                    FROM letras
                    WHERE activa = TRUE
                    ORDER BY id_letra
                    LIMIT 2;
                    """
                )
                letras = cursor.fetchall()

        if len(letras) < 2:
            self.skipTest("Se necesitan dos letras activas")

        return letras

    def leer_estado_almacenado(self):
        consultas = {
            "sesiones": """
                SELECT *
                FROM sesiones_reconocimiento
                WHERE id_usuario = ANY(%s)
                ORDER BY id_sesion;
            """,
            "resultados": """
                SELECT r.*
                FROM resultados_reconocimiento AS r
                INNER JOIN sesiones_reconocimiento AS s
                    ON s.id_sesion = r.id_sesion
                WHERE s.id_usuario = ANY(%s)
                ORDER BY r.id_resultado;
            """,
            "intentos": """
                SELECT *
                FROM intentos_reconocimiento
                WHERE id_usuario = ANY(%s)
                ORDER BY id_intento;
            """,
            "progreso": """
                SELECT *
                FROM progreso_usuario
                WHERE id_usuario = ANY(%s)
                ORDER BY id_usuario, id_letra;
            """,
        }

        estado = {}

        with obtener_conexion() as conexion:
            with conexion.cursor(row_factory=dict_row) as cursor:
                for nombre, consulta in consultas.items():
                    cursor.execute(consulta, (self.usuarios,))
                    estado[nombre] = cursor.fetchall()

        return estado

    def test_usuario_sin_historial_recibe_lista_vacia(self):
        historial = consultar_historial_usuario(self.id_usuario)

        self.assertEqual(historial, [])

    def test_incluye_sesion_sin_resultados(self):
        sesion = crear_sesion(self.id_usuario)

        historial = consultar_historial_usuario(self.id_usuario)

        self.assertEqual(historial, [{**sesion, "resultados": []}])

    def test_separa_usuarios_y_conserva_registros(self):
        letra_a, letra_b = self.obtener_letras_prueba()

        sesion_propia = crear_sesion(self.id_usuario)
        resultados_propios = []

        # Tres aciertos generan un aprendizaje real.
        for _ in range(3):
            resultado = registrar_resultado(
                id_usuario=self.id_usuario,
                id_sesion=sesion_propia["id_sesion"],
                id_letra_objetivo=letra_a["id_letra"],
                id_letra_detectada=letra_a["id_letra"],
                confianza=0.95,
            )
            resultados_propios.append(resultado)

        # También se conserva una práctica incorrecta de otra letra.
        incorrecto = registrar_resultado(
            id_usuario=self.id_usuario,
            id_sesion=sesion_propia["id_sesion"],
            id_letra_objetivo=letra_b["id_letra"],
            id_letra_detectada=letra_a["id_letra"],
            confianza=0.75,
        )
        resultados_propios.append(incorrecto)

        sesion_finalizada = finalizar_sesion(
            self.id_usuario,
            sesion_propia["id_sesion"],
        )
        sesion_vacia = crear_sesion(self.id_usuario)

        otro_usuario = self.crear_usuario_prueba()
        otra_sesion = crear_sesion(otro_usuario)

        resultado_ajeno = registrar_resultado(
            id_usuario=otro_usuario,
            id_sesion=otra_sesion["id_sesion"],
            id_letra_objetivo=letra_b["id_letra"],
            id_letra_detectada=letra_b["id_letra"],
            confianza=0.90,
        )

        antes = self.leer_estado_almacenado()

        # Evita comprobar la conservación sobre tablas vacías.
        self.assertEqual(len(antes["sesiones"]), 3)
        self.assertEqual(len(antes["resultados"]), 5)
        self.assertEqual(len(antes["intentos"]), 5)
        self.assertEqual(len(antes["progreso"]), 1)
        self.assertEqual(
            antes["progreso"][0]["id_usuario"],
            self.id_usuario,
        )
        self.assertEqual(
            antes["progreso"][0]["id_letra"],
            letra_a["id_letra"],
        )
        self.assertTrue(antes["progreso"][0]["dominada"])

        historial_propio = consultar_historial_usuario(self.id_usuario)
        historial_ajeno = consultar_historial_usuario(otro_usuario)

        nombres_letras = {
            letra_a["id_letra"]: letra_a["letra"],
            letra_b["id_letra"]: letra_b["letra"],
        }

        def resultado_esperado(resultado, id_usuario):
            return {
                **resultado,
                "id_usuario": id_usuario,
                "letra_objetivo": nombres_letras[
                    resultado["id_letra_objetivo"]
                ],
                "letra_detectada": nombres_letras[
                    resultado["id_letra_detectada"]
                ],
                "confianza": float(resultado["confianza"]),
            }

        self.assertEqual(
            historial_propio,
            [
                {**sesion_vacia, "resultados": []},
                {
                    **sesion_finalizada,
                    "resultados": [
                        resultado_esperado(resultado, self.id_usuario)
                        for resultado in reversed(resultados_propios)
                    ],
                },
            ],
        )

        self.assertEqual(
            historial_ajeno,
            [
                {
                    **otra_sesion,
                    "resultados": [
                        resultado_esperado(resultado_ajeno, otro_usuario)
                    ],
                }
            ],
        )

        # Repetir la consulta también conserva el historial.
        self.assertEqual(
            consultar_historial_usuario(self.id_usuario),
            historial_propio,
        )

        despues = self.leer_estado_almacenado()
        self.assertEqual(despues, antes)


if __name__ == "__main__":
    unittest.main()