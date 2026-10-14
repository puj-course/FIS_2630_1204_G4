import os
import unittest
from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient
from psycopg.rows import dict_row

from app.main import app
from app.security import crear_token_acceso
from app.services.resultados_service import registrar_resultado
from app.services.sesiones_service import crear_sesion, finalizar_sesion
from conf.database import obtener_conexion


@unittest.skipUnless(
    os.getenv("DATABASE_URL"),
    "Se necesita DATABASE_URL para probar PostgreSQL",
)
class TestHistorialEndpointIntegracion(unittest.TestCase):
    def setUp(self):
        self.usuarios = []
        self.addCleanup(self.eliminar_datos_prueba)

        anteriores = app.dependency_overrides.copy()
        app.dependency_overrides.clear()
        self.addCleanup(self.restaurar_overrides, anteriores)

        entorno = patch.dict(
            os.environ,
            {
                "JWT_SECRET": "clave-pruebas-integracion-historial-" * 2,
                "JWT_EXPIRE_MINUTES": "60",
                "APRENDIZAJE_MIN_ACIERTOS": "3",
            },
        )
        entorno.start()
        self.addCleanup(entorno.stop)

        self.cliente = TestClient(app)
        self.addCleanup(self.cliente.close)

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
                        "Prueba endpoint historial",
                        f"historial-http-{uuid4().hex}@signia.local",
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

        return [letra["id_letra"] for letra in letras]

    def consultar_endpoint(self, id_usuario, parametros=None):
        token = crear_token_acceso(id_usuario)

        respuesta = self.cliente.get(
            "/historial",
            headers={"Authorization": f"Bearer {token}"},
            params=parametros,
        )

        self.assertEqual(respuesta.status_code, 200, respuesta.text)
        return respuesta.json()

    def leer_datos_almacenados(self, id_usuario):
        # Consultas independientes del servicio que estamos validando.
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
                    WHERE id_usuario = %s
                    ORDER BY fecha_inicio DESC, id_sesion DESC;
                    """,
                    (id_usuario,),
                )
                sesiones = cursor.fetchall()

                cursor.execute(
                    """
                    SELECT
                        r.id_resultado,
                        r.id_sesion,
                        s.id_usuario,
                        r.id_letra_objetivo,
                        objetivo.letra AS letra_objetivo,
                        r.id_letra_detectada,
                        detectada.letra AS letra_detectada,
                        r.confianza,
                        r.es_correcto,
                        r.fecha_resultado
                    FROM resultados_reconocimiento AS r
                    INNER JOIN sesiones_reconocimiento AS s
                        ON s.id_sesion = r.id_sesion
                    INNER JOIN letras AS objetivo
                        ON objetivo.id_letra = r.id_letra_objetivo
                    INNER JOIN letras AS detectada
                        ON detectada.id_letra = r.id_letra_detectada
                    WHERE s.id_usuario = %s
                    ORDER BY r.fecha_resultado DESC, r.id_resultado DESC;
                    """,
                    (id_usuario,),
                )
                resultados = cursor.fetchall()

        return sesiones, resultados

    def comprobar_coincidencia(self, respuesta, id_usuario):
        sesiones, resultados = self.leer_datos_almacenados(id_usuario)

        self.assertEqual(set(respuesta), {"total", "historial"})
        self.assertEqual(respuesta["total"], len(sesiones))
        self.assertEqual(
            [sesion["id_sesion"] for sesion in respuesta["historial"]],
            [sesion["id_sesion"] for sesion in sesiones],
        )

        for recibida, almacenada in zip(
            respuesta["historial"],
            sesiones,
        ):
            datos_sesion = {
                campo: valor
                for campo, valor in recibida.items()
                if campo != "resultados"
            }

            for campo in ("fecha_inicio", "fecha_fin"):
                if datos_sesion[campo] is not None:
                    datos_sesion[campo] = datetime.fromisoformat(
                        datos_sesion[campo].replace("Z", "+00:00")
                    )

            self.assertEqual(datos_sesion, almacenada)

            resultados_sesion = [
                resultado
                for resultado in resultados
                if resultado["id_sesion"] == almacenada["id_sesion"]
            ]

            self.assertEqual(
                len(recibida["resultados"]),
                len(resultados_sesion),
            )

            for recibido, guardado in zip(
                recibida["resultados"],
                resultados_sesion,
            ):
                resultado_recibido = dict(recibido)
                resultado_recibido["fecha_resultado"] = (
                    datetime.fromisoformat(
                        recibido["fecha_resultado"].replace("Z", "+00:00")
                    )
                )

                resultado_guardado = {
                    **guardado,
                    "confianza": float(guardado["confianza"]),
                }

                self.assertEqual(
                    resultado_recibido,
                    resultado_guardado,
                )

    def test_usuario_sin_historial_recibe_total_cero(self):
        id_usuario = self.crear_usuario_prueba()

        respuesta = self.consultar_endpoint(id_usuario)

        self.assertEqual(respuesta, {"total": 0, "historial": []})
        self.comprobar_coincidencia(respuesta, id_usuario)

    def test_distintas_cantidades_y_usuarios_independientes(self):
        letra_a, letra_b = self.obtener_letras_prueba()
        casos = []

        for cantidad in (1, 3):
            id_usuario = self.crear_usuario_prueba()
            casos.append((id_usuario, cantidad))

            for indice in range(cantidad):
                sesion = crear_sesion(id_usuario)

                # El usuario con tres sesiones conserva una sesión vacía.
                if cantidad > 1 and indice == cantidad - 1:
                    continue

                for detectada in (letra_a, letra_b):
                    registrar_resultado(
                        id_usuario=id_usuario,
                        id_sesion=sesion["id_sesion"],
                        id_letra_objetivo=letra_a,
                        id_letra_detectada=detectada,
                        confianza=0.90,
                    )

                if indice == 0:
                    finalizar_sesion(
                        id_usuario,
                        sesion["id_sesion"],
                    )

        # Consultamos cuando ambos usuarios ya tienen datos almacenados.
        historiales = {}

        for id_usuario, cantidad in casos:
            with self.subTest(sesiones=cantidad):
                respuesta = self.consultar_endpoint(id_usuario)

                self.assertEqual(respuesta["total"], cantidad)
                self.comprobar_coincidencia(respuesta, id_usuario)
                historiales[id_usuario] = respuesta

        usuario_a = casos[0][0]
        usuario_b = casos[1][0]

        sesiones_a = {
            sesion["id_sesion"]
            for sesion in historiales[usuario_a]["historial"]
        }
        sesiones_b = {
            sesion["id_sesion"]
            for sesion in historiales[usuario_b]["historial"]
        }
        self.assertTrue(sesiones_a.isdisjoint(sesiones_b))

        # Un identificador ajeno en la URL no cambia al dueño del token.
        for propietario, ajeno in (
            (usuario_a, usuario_b),
            (usuario_b, usuario_a),
        ):
            with self.subTest(propietario=propietario):
                respuesta = self.consultar_endpoint(
                    propietario,
                    parametros={"id_usuario": ajeno},
                )
                self.assertEqual(respuesta, historiales[propietario])

    def test_rechaza_consulta_sin_autenticacion(self):
        for cabeceras in (
            {},
            {"Authorization": "Bearer token-invalido"},
        ):
            with self.subTest(cabeceras=cabeceras):
                respuesta = self.cliente.get(
                    "/historial",
                    headers=cabeceras,
                )

                self.assertEqual(
                    respuesta.status_code,
                    401,
                    respuesta.text,
                )
                self.assertEqual(
                    respuesta.json(),
                    {"detail": "No fue posible validar las credenciales"},
                )
                self.assertEqual(
                    respuesta.headers.get("www-authenticate"),
                    "Bearer",
                )


if __name__ == "__main__":
    unittest.main()