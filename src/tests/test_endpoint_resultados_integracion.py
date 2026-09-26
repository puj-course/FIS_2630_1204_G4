import os
import unittest
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient
from psycopg.rows import dict_row

from app.main import app
from app.security import crear_token_acceso
from app.services.sesiones_service import crear_sesion
from conf.database import obtener_conexion
from src.schemas.resultados import ResultadoRegistrado


@unittest.skipUnless(
    os.getenv("DATABASE_URL"),
    "Se necesita DATABASE_URL para probar PostgreSQL",
)
class TestEndpointResultadosIntegracion(unittest.TestCase):
    def setUp(self):
        self.usuarios = []
        self.addCleanup(self.eliminar_datos_prueba)

        # Conserva y restaura las dependencias de otras pruebas.
        anteriores = app.dependency_overrides.copy()
        app.dependency_overrides.clear()
        self.addCleanup(self.restaurar_overrides, anteriores)

        # Usa una clave exclusiva de estas pruebas.
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
        self.sesion = crear_sesion(self.id_usuario)

        token = crear_token_acceso(self.id_usuario)
        self.cabeceras = {
            "Authorization": f"Bearer {token}",
        }

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
                        "Prueba endpoint resultados",
                        f"resultados-{uuid4().hex}@signia.local",
                        "hash-solo-para-pruebas",
                    ),
                )
                id_usuario = cursor.fetchone()["id_usuario"]

        self.usuarios.append(id_usuario)
        return id_usuario

    def eliminar_datos_prueba(self):
        if not self.usuarios:
            return

        # Las sesiones y sus resultados se eliminan por cascada.
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
        # Abre otra conexión para comprobar datos confirmados.
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

    def test_guarda_acierto_y_error_en_la_misma_sesion(self):
        resultados_api = []

        for detectada, correcto in (
            (self.id_letra_a, True),
            (self.id_letra_b, False),
        ):
            with self.subTest(es_correcto=correcto):
                datos = {
                    **self.datos,
                    "id_letra_detectada": detectada,
                }

                respuesta = self.cliente.post(
                    "/resultados",
                    headers=self.cabeceras,
                    json=datos,
                )

                self.assertEqual(
                    respuesta.status_code,
                    201,
                    respuesta.text,
                )
                self.assertEqual(
                    respuesta.json()["mensaje"],
                    "Resultado registrado correctamente",
                )

                resultado = respuesta.json()["resultado"]

                for campo, valor in datos.items():
                    self.assertEqual(resultado[campo], valor)

                self.assertIs(resultado["es_correcto"], correcto)
                resultados_api.append(resultado)

        almacenados = self.leer_resultados(
            self.sesion["id_sesion"]
        )

        self.assertEqual(len(almacenados), 2)
        self.assertNotEqual(
            almacenados[0]["id_resultado"],
            almacenados[1]["id_resultado"],
        )

        for almacenado, recibido in zip(
            almacenados,
            resultados_api,
        ):
            self.assertIsNotNone(
                almacenado["fecha_resultado"].utcoffset()
            )
            self.assertEqual(
                ResultadoRegistrado.model_validate(almacenado),
                ResultadoRegistrado.model_validate(recibido),
            )

    def test_rechaza_sesion_ajena_sin_guardar_resultados(self):
        otro_usuario = self.crear_usuario_prueba()
        ajena = crear_sesion(otro_usuario)

        respuesta = self.cliente.post(
            "/resultados",
            headers=self.cabeceras,
            json={
                **self.datos,
                "id_sesion": ajena["id_sesion"],
            },
        )

        self.assertEqual(respuesta.status_code, 403, respuesta.text)
        self.assertEqual(
            self.leer_resultados(ajena["id_sesion"]),
            [],
        )
        self.assertEqual(
            self.leer_resultados(self.sesion["id_sesion"]),
            [],
        )

    def test_rechaza_sesion_inexistente(self):
        # Elimina una sesión propia de prueba para obtener
        # un identificador inexistente sin adivinarlo.
        eliminada = crear_sesion(self.id_usuario)

        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM sesiones_reconocimiento
                    WHERE id_sesion = %s AND id_usuario = %s;
                    """,
                    (
                        eliminada["id_sesion"],
                        self.id_usuario,
                    ),
                )

        respuesta = self.cliente.post(
            "/resultados",
            headers=self.cabeceras,
            json={
                **self.datos,
                "id_sesion": eliminada["id_sesion"],
            },
        )

        self.assertEqual(respuesta.status_code, 404, respuesta.text)
        self.assertEqual(
            self.leer_resultados(eliminada["id_sesion"]),
            [],
        )

    def test_rechaza_solicitud_sin_token(self):
        respuesta = self.cliente.post(
            "/resultados",
            json=self.datos,
        )

        self.assertEqual(respuesta.status_code, 401, respuesta.text)
        self.assertEqual(
            self.leer_resultados(self.sesion["id_sesion"]),
            [],
        )

    def test_rechaza_datos_invalidos_sin_guardarlos(self):
        respuesta = self.cliente.post(
            "/resultados",
            headers=self.cabeceras,
            json={
                **self.datos,
                "confianza": 1.5,
            },
        )

        self.assertEqual(respuesta.status_code, 422, respuesta.text)
        self.assertEqual(
            self.leer_resultados(self.sesion["id_sesion"]),
            [],
        )


if __name__ == "__main__":
    unittest.main()