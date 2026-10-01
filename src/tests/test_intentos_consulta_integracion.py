import os
import unittest
from unittest.mock import patch
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from psycopg.rows import dict_row

from app.routes.intentos import router
from app.security import crear_token_acceso
from app.services.resultados_service import registrar_resultado
from app.services.sesiones_service import crear_sesion
from conf.database import obtener_conexion
from src.schemas.intentos import IntentoRegistrado


@unittest.skipUnless(
    os.getenv("DATABASE_URL"),
    "Se requiere DATABASE_URL para las pruebas de integración",
)
class TestConsultaIntentosIntegracion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.usuarios_creados = []
        cls.addClassCleanup(cls.eliminar_datos_prueba)

        entorno = patch.dict(
            os.environ,
            {
                "JWT_SECRET": (
                    "clave-exclusiva-pruebas-consulta-intentos-373"
                ),
                "JWT_EXPIRE_MINUTES": "60",
            },
        )
        entorno.start()
        cls.addClassCleanup(entorno.stop)

        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
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
            raise unittest.SkipTest(
                "Se necesitan al menos dos letras activas"
            )

        cls.letra_a = letras[0][0]
        cls.letra_b = letras[1][0]

        cls.usuario_a = cls.crear_usuario_prueba()
        cls.usuario_b = cls.crear_usuario_prueba()

        cls.sesion_a1 = crear_sesion(cls.usuario_a)["id_sesion"]
        cls.sesion_a2 = crear_sesion(cls.usuario_a)["id_sesion"]
        cls.sesion_b = crear_sesion(cls.usuario_b)["id_sesion"]
        cls.sesion_vacia = crear_sesion(cls.usuario_a)["id_sesion"]

        # Obtiene un identificador inexistente sin asumir un valor.
        cls.sesion_eliminada = crear_sesion(
            cls.usuario_a
        )["id_sesion"]

        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM sesiones_reconocimiento
                    WHERE id_sesion = %s AND id_usuario = %s;
                    """,
                    (cls.sesion_eliminada, cls.usuario_a),
                )

        casos = [
            (
                cls.usuario_a,
                cls.sesion_a1,
                cls.letra_a,
                cls.letra_a,
            ),
            (
                cls.usuario_a,
                cls.sesion_a1,
                cls.letra_b,
                cls.letra_a,
            ),
            (
                cls.usuario_a,
                cls.sesion_a2,
                cls.letra_a,
                cls.letra_b,
            ),
            (
                cls.usuario_a,
                cls.sesion_a2,
                cls.letra_b,
                cls.letra_b,
            ),
            (
                cls.usuario_b,
                cls.sesion_b,
                cls.letra_a,
                cls.letra_a,
            ),
        ]

        cls.intentos_esperados = []

        for usuario, sesion, objetivo, detectada in casos:
            resultado = registrar_resultado(
                id_usuario=usuario,
                id_sesion=sesion,
                id_letra_objetivo=objetivo,
                id_letra_detectada=detectada,
                confianza=0.95,
            )

            # Lee desde otra conexión después de guardar el resultado.
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
                        WHERE id_resultado = %s;
                        """,
                        (resultado["id_resultado"],),
                    )
                    intentos = cursor.fetchall()

            if len(intentos) != 1:
                raise AssertionError(
                    "Cada resultado de prueba debe tener un intento"
                )

            intento = IntentoRegistrado.model_validate(intentos[0])

            if (
                intento.id_usuario != usuario
                or intento.id_sesion != sesion
                or intento.id_letra != objetivo
                or intento.es_correcto != (objetivo == detectada)
            ):
                raise AssertionError(
                    "El intento almacenado no coincide con el resultado"
                )

            cls.intentos_esperados.append(intento)

        cls.cabeceras_a = {
            "Authorization": (
                f"Bearer {crear_token_acceso(cls.usuario_a)}"
            ),
        }
        cls.cabeceras_b = {
            "Authorization": (
                f"Bearer {crear_token_acceso(cls.usuario_b)}"
            ),
        }

        # Usa la ruta y la autenticación reales, sin reemplazar servicios.
        aplicacion = FastAPI()
        aplicacion.include_router(router)

        cls.cliente = TestClient(aplicacion)
        cls.addClassCleanup(cls.cliente.close)

    @classmethod
    def crear_usuario_prueba(cls):
        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO usuarios (
                        nombre,
                        correo,
                        contrasena_hash,
                        rol
                    )
                    VALUES (%s, %s, %s, %s)
                    RETURNING id_usuario;
                    """,
                    (
                        "Prueba consulta intentos",
                        f"intentos-{uuid4().hex}@example.com",
                        "hash-exclusivo-de-prueba",
                        "usuario",
                    ),
                )
                id_usuario = cursor.fetchone()[0]

        cls.usuarios_creados.append(id_usuario)
        return id_usuario

    @classmethod
    def eliminar_datos_prueba(cls):
        if not cls.usuarios_creados:
            return

        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM usuarios
                    WHERE id_usuario = ANY(%s);
                    """,
                    (cls.usuarios_creados,),
                )

    def comprobar_consulta(
        self,
        usuario,
        cabeceras,
        parametros=None,
    ):
        filtros = parametros or {}

        respuesta = self.cliente.get(
            "/intentos",
            headers=cabeceras,
            params=filtros,
        )

        self.assertEqual(
            respuesta.status_code,
            200,
            respuesta.text,
        )

        esperados = [
            intento
            for intento in self.intentos_esperados
            if intento.id_usuario == usuario
            and (
                "id_letra" not in filtros
                or intento.id_letra == filtros["id_letra"]
            )
            and (
                "id_sesion" not in filtros
                or intento.id_sesion == filtros["id_sesion"]
            )
        ]

        esperados.sort(
            key=lambda intento: (
                intento.fecha_intento,
                intento.id_intento,
            ),
            reverse=True,
        )

        contenido = respuesta.json()

        self.assertEqual(contenido["total"], len(esperados))
        self.assertEqual(
            [
                IntentoRegistrado.model_validate(intento)
                for intento in contenido["intentos"]
            ],
            esperados,
        )

        return contenido

    def test_consulta_separa_los_usuarios(self):
        casos = [
            (self.usuario_a, self.cabeceras_a, 4),
            (self.usuario_b, self.cabeceras_b, 1),
        ]

        for usuario, cabeceras, cantidad in casos:
            with self.subTest(usuario=usuario):
                contenido = self.comprobar_consulta(
                    usuario,
                    cabeceras,
                )

                self.assertEqual(contenido["total"], cantidad)

    def test_filtra_por_letra_sesion_y_ambos(self):
        casos = [
            ({"id_letra": self.letra_a}, 2),
            ({"id_letra": self.letra_b}, 2),
            ({"id_sesion": self.sesion_a1}, 2),
            ({"id_sesion": self.sesion_a2}, 2),
            (
                {
                    "id_letra": self.letra_a,
                    "id_sesion": self.sesion_a1,
                },
                1,
            ),
            (
                {
                    "id_letra": self.letra_b,
                    "id_sesion": self.sesion_a2,
                },
                1,
            ),
        ]

        for filtros, cantidad in casos:
            with self.subTest(filtros=filtros):
                contenido = self.comprobar_consulta(
                    self.usuario_a,
                    self.cabeceras_a,
                    filtros,
                )

                self.assertEqual(contenido["total"], cantidad)

    def test_sesion_vacia_o_inexistente_devuelve_lista_vacia(self):
        for sesion in (self.sesion_vacia, self.sesion_eliminada):
            with self.subTest(sesion=sesion):
                contenido = self.comprobar_consulta(
                    self.usuario_a,
                    self.cabeceras_a,
                    {"id_sesion": sesion},
                )

                self.assertEqual(
                    contenido,
                    {"total": 0, "intentos": []},
                )

    def test_no_expone_intentos_de_sesion_ajena(self):
        contenido = self.comprobar_consulta(
            self.usuario_a,
            self.cabeceras_a,
            {
                "id_sesion": self.sesion_b,
                "id_usuario": self.usuario_b,
            },
        )

        self.assertEqual(
            contenido,
            {"total": 0, "intentos": []},
        )

    def test_usuario_en_url_no_reemplaza_al_autenticado(self):
        contenido = self.comprobar_consulta(
            self.usuario_a,
            self.cabeceras_a,
            {"id_usuario": self.usuario_b},
        )

        self.assertEqual(contenido["total"], 4)


if __name__ == "__main__":
    unittest.main()