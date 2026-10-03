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
class TestResultadosProgresoIntegracion(unittest.TestCase):
    def setUp(self):
        self.usuarios = []
        self.addCleanup(self.eliminar_datos_prueba)

        anteriores = app.dependency_overrides.copy()
        app.dependency_overrides.clear()
        self.addCleanup(self.restaurar_overrides, anteriores)

        parche = patch.dict(
            os.environ,
            {
                "JWT_SECRET": "clave-exclusiva-pruebas-resultados-" * 2,
                "JWT_EXPIRE_MINUTES": "60",
            },
        )
        parche.start()
        self.addCleanup(parche.stop)

        self.cliente = TestClient(app)
        self.addCleanup(self.cliente.close)

        with obtener_conexion() as conexion:
            with conexion.cursor(row_factory=dict_row) as cursor:
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
            self.skipTest("Se necesitan dos letras activas")

        self.id_letra_a = letras[0]["id_letra"]
        self.id_letra_b = letras[1]["id_letra"]

        self.id_usuario = self.crear_usuario_prueba()

        token = crear_token_acceso(self.id_usuario)
        self.cabeceras = {
            "Authorization": f"Bearer {token}",
        }

        respuesta = self.cliente.post(
            "/sesiones",
            headers=self.cabeceras,
        )

        self.assertEqual(
            respuesta.status_code,
            201,
            respuesta.text,
        )

        self.sesion = respuesta.json()["sesion"]

        self.assertEqual(
            self.sesion["id_usuario"],
            self.id_usuario,
        )
        self.assertEqual(self.sesion["estado"], "activa")
        self.assertIsNone(self.sesion["fecha_fin"])

        self.datos = {
            "id_sesion": self.sesion["id_sesion"],
            "id_letra_objetivo": self.id_letra_a,
            "id_letra_detectada": self.id_letra_a,
            "confianza": 0.95,
        }

    def restaurar_overrides(self, anteriores):
        app.dependency_overrides.clear()
        app.dependency_overrides.update(anteriores)

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
                        "Prueba integración resultados y progreso",
                        f"resultados-progreso-{uuid4().hex}@signia.local",
                        "hash-solo-para-pruebas",
                    ),
                )
                id_usuario = cursor.fetchone()["id_usuario"]

        self.usuarios.append(id_usuario)
        return id_usuario

    def eliminar_datos_prueba(self):
        if not self.usuarios:
            return

        # Elimina por cascada los datos de los usuarios de prueba.
        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM usuarios
                    WHERE id_usuario = ANY(%s);
                    """,
                    (self.usuarios,),
                )

    def leer_resultados(self, id_sesion):
        # Consulta desde una conexión independiente.
        with obtener_conexion() as conexion:
            with conexion.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT
                        id_resultado,
                        id_sesion,
                        id_letra_objetivo,
                        id_letra_detectada,
                        confianza,
                        es_correcto,
                        fecha_resultado
                    FROM resultados_reconocimiento
                    WHERE id_sesion = %s
                    ORDER BY id_resultado;
                    """,
                    (id_sesion,),
                )

                return cursor.fetchall()

    def leer_intentos(self, id_sesion):
        with obtener_conexion() as conexion:
            with conexion.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT
                        id_intento,
                        id_resultado,
                        id_usuario,
                        id_sesion,
                        id_letra,
                        es_correcto,
                        fecha_intento
                    FROM intentos_reconocimiento
                    WHERE id_sesion = %s
                    ORDER BY id_intento;
                    """,
                    (id_sesion,),
                )

                return cursor.fetchall()

    def leer_progreso(self, id_usuario):
        with obtener_conexion() as conexion:
            with conexion.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT *
                    FROM progreso_usuario
                    WHERE id_usuario = %s
                    ORDER BY id_letra;
                    """,
                    (id_usuario,),
                )
                return cursor.fetchall()

    def registrar_resultado(self, datos=None, cabeceras=None):
        respuesta = self.cliente.post(
            "/resultados",
            headers=self.cabeceras if cabeceras is None else cabeceras,
            json=self.datos if datos is None else datos,
        )
        self.assertEqual(respuesta.status_code, 201, respuesta.text)
        return respuesta.json()["resultado"]

    def test_actualiza_solo_al_usuario_de_cada_sesion(self):
        otro_usuario = self.crear_usuario_prueba()
        token = crear_token_acceso(otro_usuario)
        otras_cabeceras = {"Authorization": f"Bearer {token}"}
        respuesta = self.cliente.post("/sesiones", headers=otras_cabeceras)
        self.assertEqual(respuesta.status_code, 201, respuesta.text)
        otra_sesion = respuesta.json()["sesion"]

        resultado = self.registrar_resultado()
        self.assertTrue(resultado["es_correcto"])
        progreso = self.leer_progreso(self.id_usuario)
        self.assertEqual(len(progreso), 1)
        self.assertEqual(progreso[0]["id_usuario"], self.id_usuario)
        self.assertEqual(progreso[0]["id_letra"], self.id_letra_a)
        self.assertTrue(progreso[0]["dominada"])
        self.assertEqual(self.leer_progreso(otro_usuario), [])

        otros_datos = {
            **self.datos,
            "id_sesion": otra_sesion["id_sesion"],
            "id_letra_objetivo": self.id_letra_b,
            "id_letra_detectada": self.id_letra_b,
        }
        self.registrar_resultado(otros_datos, otras_cabeceras)
        otro_progreso = self.leer_progreso(otro_usuario)
        self.assertEqual(len(otro_progreso), 1)
        self.assertEqual(otro_progreso[0]["id_usuario"], otro_usuario)
        self.assertEqual(otro_progreso[0]["id_letra"], self.id_letra_b)
        self.assertTrue(otro_progreso[0]["dominada"])
        self.assertEqual(self.leer_progreso(self.id_usuario), progreso)

    def test_resultado_incorrecto_no_crea_ni_modifica_progreso(self):
        incorrectos = {**self.datos, "id_letra_detectada": self.id_letra_b}
        resultado = self.registrar_resultado(incorrectos)
        self.assertFalse(resultado["es_correcto"])
        self.assertEqual(self.leer_progreso(self.id_usuario), [])

        self.registrar_resultado()
        anterior = self.leer_progreso(self.id_usuario)
        self.assertEqual(len(anterior), 1)
        self.registrar_resultado(incorrectos)
        self.assertEqual(self.leer_progreso(self.id_usuario), anterior)

    def test_aciertos_repetidos_no_duplican_progreso(self):
        primero = self.registrar_resultado()
        inicial = self.leer_progreso(self.id_usuario)
        self.assertEqual(len(inicial), 1)
        segundo = self.registrar_resultado()
        final = self.leer_progreso(self.id_usuario)

        self.assertNotEqual(primero["id_resultado"], segundo["id_resultado"])
        self.assertEqual(len(final), 1)
        self.assertEqual(final[0]["id_progreso"], inicial[0]["id_progreso"])
        self.assertTrue(final[0]["dominada"])
        self.assertEqual(len(self.leer_intentos(self.sesion["id_sesion"])), 2)

    def test_error_de_progreso_conserva_resultado_e_intento_confirmados(self):
        observados = {}

        def fallar_progreso(**kwargs):
            # Otra conexión debe poder ver los registros antes del fallo.
            observados["argumentos"] = kwargs
            observados["resultados"] = self.leer_resultados(
                self.sesion["id_sesion"]
            )
            observados["intentos"] = self.leer_intentos(
                self.sesion["id_sesion"]
            )
            raise RuntimeError("Fallo simulado al actualizar progreso")

        with patch(
            "app.services.resultados_service.registrar_progreso",
            side_effect=fallar_progreso,
        ) as actualizar:
            with self.assertLogs(
                "app.services.resultados_service", level="ERROR"
            ):
                resultado = self.registrar_resultado()

        actualizar.assert_called_once_with(
            id_usuario=self.id_usuario, id_letra=self.id_letra_a
        )
        self.assertEqual(
            observados["argumentos"],
            {"id_usuario": self.id_usuario, "id_letra": self.id_letra_a},
        )
        self.assertEqual(len(observados["resultados"]), 1)
        self.assertEqual(len(observados["intentos"]), 1)
        guardado = observados["resultados"][0]
        intento = observados["intentos"][0]
        self.assertEqual(guardado["id_resultado"], resultado["id_resultado"])
        self.assertEqual(intento["id_resultado"], resultado["id_resultado"])
        self.assertEqual(intento["id_usuario"], self.id_usuario)
        self.assertEqual(intento["id_sesion"], self.sesion["id_sesion"])
        self.assertTrue(intento["es_correcto"])
        self.assertEqual(
            self.leer_resultados(self.sesion["id_sesion"]),
            observados["resultados"],
        )
        self.assertEqual(
            self.leer_intentos(self.sesion["id_sesion"]),
            observados["intentos"],
        )
        self.assertEqual(self.leer_progreso(self.id_usuario), [])


if __name__ == "__main__":
    unittest.main()
