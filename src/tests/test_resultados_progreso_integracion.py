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
                "APRENDIZAJE_MIN_ACIERTOS": "3",
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

        respuesta = self.cliente.post(
            "/sesiones",
            headers=otras_cabeceras,
        )
        self.assertEqual(respuesta.status_code, 201, respuesta.text)
        otra_sesion = respuesta.json()["sesion"]
        self.assertEqual(otra_sesion["id_usuario"], otro_usuario)

        # Los primeros dos aciertos todavía no generan aprendizaje.
        for numero_acierto in range(1, 4):
            with self.subTest(
                usuario=self.id_usuario,
                acierto=numero_acierto,
            ):
                resultado = self.registrar_resultado()
                self.assertTrue(resultado["es_correcto"])

                if numero_acierto < 3:
                    self.assertEqual(
                        self.leer_progreso(self.id_usuario),
                        [],
                    )

                self.assertEqual(
                    self.leer_progreso(otro_usuario),
                    [],
                )

        progreso = self.leer_progreso(self.id_usuario)
        self.assertEqual(len(progreso), 1)
        self.assertEqual(progreso[0]["id_usuario"], self.id_usuario)
        self.assertEqual(progreso[0]["id_letra"], self.id_letra_a)
        self.assertTrue(progreso[0]["dominada"])
        otros_datos = {
            **self.datos,
            "id_sesion": otra_sesion["id_sesion"],
            "id_letra_objetivo": self.id_letra_b,
            "id_letra_detectada": self.id_letra_b,
        }

        # El segundo usuario debe alcanzar su propio mínimo.
        for numero_acierto in range(1, 4):
            with self.subTest(
                usuario=otro_usuario,
                acierto=numero_acierto,
            ):
                resultado = self.registrar_resultado(
                    otros_datos,
                    otras_cabeceras,
                )
                self.assertTrue(resultado["es_correcto"])

                if numero_acierto < 3:
                    self.assertEqual(
                        self.leer_progreso(otro_usuario),
                        [],
                    )

                self.assertEqual(
                    self.leer_progreso(self.id_usuario),
                    progreso,
                )

        otro_progreso = self.leer_progreso(otro_usuario)
        self.assertEqual(len(otro_progreso), 1)
        self.assertEqual(otro_progreso[0]["id_usuario"], otro_usuario)
        self.assertEqual(otro_progreso[0]["id_letra"], self.id_letra_b)
        self.assertTrue(otro_progreso[0]["dominada"])

    def test_resultado_incorrecto_no_crea_ni_modifica_progreso(self):
        incorrectos = {
            **self.datos,
            "id_letra_detectada": self.id_letra_b,
        }

        resultado = self.registrar_resultado(incorrectos)
        self.assertFalse(resultado["es_correcto"])
        self.assertEqual(self.leer_progreso(self.id_usuario), [])

        # Dos aciertos no son suficientes, aunque exista un intento fallido.
        for _ in range(2):
            resultado = self.registrar_resultado()
            self.assertTrue(resultado["es_correcto"])
            self.assertEqual(self.leer_progreso(self.id_usuario), [])

        # Un error intermedio no suma aciertos ni reinicia los acumulados.
        resultado = self.registrar_resultado(incorrectos)
        self.assertFalse(resultado["es_correcto"])
        self.assertEqual(self.leer_progreso(self.id_usuario), [])

        resultado = self.registrar_resultado()
        self.assertTrue(resultado["es_correcto"])

        anterior = self.leer_progreso(self.id_usuario)
        self.assertEqual(len(anterior), 1)
        self.assertEqual(anterior[0]["id_usuario"], self.id_usuario)
        self.assertEqual(anterior[0]["id_letra"], self.id_letra_a)
        self.assertTrue(anterior[0]["dominada"])

        # Una vez aprendida, un error tampoco modifica el registro.
        resultado = self.registrar_resultado(incorrectos)
        self.assertFalse(resultado["es_correcto"])
        self.assertEqual(
            self.leer_progreso(self.id_usuario),
            anterior,
        )

        intentos = self.leer_intentos(self.sesion["id_sesion"])
        self.assertEqual(len(intentos), 6)
        self.assertEqual(
            sum(intento["es_correcto"] for intento in intentos),
            3,
        )

    def test_aciertos_repetidos_no_duplican_progreso(self):
        resultados = []

        for numero_acierto in range(1, 4):
            resultado = self.registrar_resultado()
            self.assertTrue(resultado["es_correcto"])
            resultados.append(resultado)

            if numero_acierto < 3:
                self.assertEqual(
                    self.leer_progreso(self.id_usuario),
                    [],
                )

        inicial = self.leer_progreso(self.id_usuario)
        self.assertEqual(len(inicial), 1)
        self.assertEqual(inicial[0]["id_usuario"], self.id_usuario)
        self.assertEqual(inicial[0]["id_letra"], self.id_letra_a)
        self.assertTrue(inicial[0]["dominada"])

        # El cuarto acierto guarda otro intento, pero no cambia el progreso.
        adicional = self.registrar_resultado()
        self.assertTrue(adicional["es_correcto"])
        resultados.append(adicional)

        final = self.leer_progreso(self.id_usuario)

        # Compara todos los campos, incluida fecha_actualizacion.
        self.assertEqual(final, inicial)
        self.assertEqual(
            len({resultado["id_resultado"] for resultado in resultados}),
            4,
        )

        intentos = self.leer_intentos(self.sesion["id_sesion"])
        self.assertEqual(len(intentos), 4)
        self.assertTrue(all(intento["es_correcto"] for intento in intentos))
        self.assertEqual(
            {intento["id_resultado"] for intento in intentos},
            {resultado["id_resultado"] for resultado in resultados},
        )
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
            "app.services.resultados_service.evaluar_aprendizaje",
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
    def test_acumula_aciertos_entre_sesiones_del_mismo_usuario(self):
        for _ in range(2):
            self.registrar_resultado()

        self.assertEqual(self.leer_progreso(self.id_usuario), [])

        # Prepara una segunda sesión sin depender del endpoint de cierre.
        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE sesiones_reconocimiento
                    SET
                        estado = 'finalizada',
                        fecha_fin = CURRENT_TIMESTAMP
                    WHERE id_sesion = %s
                        AND id_usuario = %s;
                    """,
                    (self.sesion["id_sesion"], self.id_usuario),
                )
                self.assertEqual(cursor.rowcount, 1)

        respuesta = self.cliente.post(
            "/sesiones",
            headers=self.cabeceras,
        )
        self.assertEqual(respuesta.status_code, 201, respuesta.text)
        nueva_sesion = respuesta.json()["sesion"]

        self.assertNotEqual(
            nueva_sesion["id_sesion"],
            self.sesion["id_sesion"],
        )
        self.assertEqual(nueva_sesion["id_usuario"], self.id_usuario)
        self.assertEqual(nueva_sesion["estado"], "activa")

        resultado = self.registrar_resultado(
            {
                **self.datos,
                "id_sesion": nueva_sesion["id_sesion"],
            }
        )
        self.assertTrue(resultado["es_correcto"])

        progreso = self.leer_progreso(self.id_usuario)
        self.assertEqual(len(progreso), 1)
        self.assertEqual(progreso[0]["id_usuario"], self.id_usuario)
        self.assertEqual(progreso[0]["id_letra"], self.id_letra_a)
        self.assertTrue(progreso[0]["dominada"])

        anteriores = self.leer_intentos(self.sesion["id_sesion"])
        nuevos = self.leer_intentos(nueva_sesion["id_sesion"])

        self.assertEqual(len(anteriores), 2)
        self.assertEqual(len(nuevos), 1)
        self.assertEqual(
            nuevos[0]["id_resultado"],
            resultado["id_resultado"],
        )

        for intento in anteriores + nuevos:
            self.assertEqual(intento["id_usuario"], self.id_usuario)
            self.assertEqual(intento["id_letra"], self.id_letra_a)
            self.assertTrue(intento["es_correcto"])
    def test_cuenta_aciertos_independientemente_por_letra(self):
        datos_b = {
            **self.datos,
            "id_letra_objetivo": self.id_letra_b,
            "id_letra_detectada": self.id_letra_b,
        }

        for _ in range(2):
            self.registrar_resultado()
            self.registrar_resultado(datos_b)

        self.assertEqual(self.leer_progreso(self.id_usuario), [])

        # Solo la primera letra alcanza tres aciertos.
        self.registrar_resultado()

        progreso_a = self.leer_progreso(self.id_usuario)
        self.assertEqual(len(progreso_a), 1)
        self.assertEqual(progreso_a[0]["id_letra"], self.id_letra_a)
        self.assertTrue(progreso_a[0]["dominada"])

        # La segunda letra necesita su tercer acierto.
        self.registrar_resultado(datos_b)

        progreso_final = self.leer_progreso(self.id_usuario)
        self.assertEqual(len(progreso_final), 2)

        por_letra = {
            registro["id_letra"]: registro
            for registro in progreso_final
        }
        self.assertEqual(
            set(por_letra),
            {self.id_letra_a, self.id_letra_b},
        )
        self.assertEqual(por_letra[self.id_letra_a], progreso_a[0])

        for registro in progreso_final:
            self.assertEqual(registro["id_usuario"], self.id_usuario)
            self.assertTrue(registro["dominada"])

        intentos = self.leer_intentos(self.sesion["id_sesion"])
        self.assertEqual(len(intentos), 6)

        for id_letra in (self.id_letra_a, self.id_letra_b):
            aciertos = sum(
                intento["es_correcto"]
                for intento in intentos
                if intento["id_letra"] == id_letra
            )
            self.assertEqual(aciertos, 3)
    def test_respeta_minimo_configurado_y_conserva_aprendizaje(self):
        with patch.dict(
            os.environ,
            {"APRENDIZAJE_MIN_ACIERTOS": "5"},
        ):
            for numero_acierto in range(1, 5):
                with self.subTest(acierto=numero_acierto):
                    resultado = self.registrar_resultado()
                    self.assertTrue(resultado["es_correcto"])
                    self.assertEqual(
                        self.leer_progreso(self.id_usuario),
                        [],
                    )

            self.registrar_resultado()

        aprendido = self.leer_progreso(self.id_usuario)
        self.assertEqual(len(aprendido), 1)
        self.assertEqual(aprendido[0]["id_usuario"], self.id_usuario)
        self.assertEqual(aprendido[0]["id_letra"], self.id_letra_a)
        self.assertTrue(aprendido[0]["dominada"])

        with patch.dict(
            os.environ,
            {"APRENDIZAJE_MIN_ACIERTOS": "7"},
        ):
            for numero_acierto in (6, 7):
                with self.subTest(acierto=numero_acierto):
                    self.registrar_resultado()

                    # También conserva la fecha de actualización.
                    self.assertEqual(
                        self.leer_progreso(self.id_usuario),
                        aprendido,
                    )

        intentos = self.leer_intentos(self.sesion["id_sesion"])
        self.assertEqual(len(intentos), 7)
        self.assertTrue(all(intento["es_correcto"] for intento in intentos))
    def test_perfil_refleja_porcentaje_solo_al_aprender_la_letra(self):
        with obtener_conexion() as conexion:
            with conexion.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*) AS total
                    FROM letras
                    WHERE activa = TRUE;
                    """
                )
                total_letras = cursor.fetchone()["total"]

        self.assertGreaterEqual(total_letras, 2)

        def consultar_perfil():
            respuesta = self.cliente.get(
                "/perfil",
                headers=self.cabeceras,
            )
            self.assertEqual(
                respuesta.status_code,
                200,
                respuesta.text,
            )
            perfil = respuesta.json()
            self.assertEqual(perfil["id_usuario"], self.id_usuario)
            self.assertEqual(
                perfil["progreso"]["total_letras"],
                total_letras,
            )
            return perfil["progreso"]

        inicial = consultar_perfil()
        self.assertEqual(inicial["letras_dominadas"], 0)
        self.assertEqual(inicial["porcentaje_progreso"], 0.0)

        for numero_acierto in (1, 2):
            with self.subTest(acierto=numero_acierto):
                self.registrar_resultado()
                pendiente = consultar_perfil()
                self.assertEqual(pendiente["letras_dominadas"], 0)
                self.assertEqual(
                    pendiente["porcentaje_progreso"],
                    0.0,
                )

        self.registrar_resultado()

        aprendido = consultar_perfil()
        porcentaje_esperado = round(100 / total_letras, 2)

        self.assertEqual(aprendido["letras_dominadas"], 1)
        self.assertEqual(
            aprendido["porcentaje_progreso"],
            porcentaje_esperado,
        )

        # Comprueba también el registro almacenado en otra conexión.
        almacenado = self.leer_progreso(self.id_usuario)
        self.assertEqual(len(almacenado), 1)
        self.assertEqual(almacenado[0]["id_letra"], self.id_letra_a)
        self.assertTrue(almacenado[0]["dominada"])

        # Repetir una letra aprendida no aumenta el porcentaje.
        self.registrar_resultado()
        repetido = consultar_perfil()

        self.assertEqual(repetido["letras_dominadas"], 1)
        self.assertEqual(
            repetido["porcentaje_progreso"],
            porcentaje_esperado,
        )
        self.assertEqual(
            self.leer_progreso(self.id_usuario),
            almacenado,
        )
    def test_configuracion_invalida_conserva_datos_y_permite_recuperacion(self):
        for _ in range(2):
            self.registrar_resultado()

        self.assertEqual(self.leer_progreso(self.id_usuario), [])

        with patch.dict(
            os.environ,
            {"APRENDIZAJE_MIN_ACIERTOS": "0"},
        ):
            with self.assertLogs(
                "app.services.resultados_service",
                level="ERROR",
            ) as registros:
                tercero = self.registrar_resultado()

        self.assertTrue(tercero["es_correcto"])
        self.assertTrue(
            any(
                "ConfiguracionAprendizajeError" in mensaje
                for mensaje in registros.output
            )
        )

        resultados = self.leer_resultados(self.sesion["id_sesion"])
        intentos = self.leer_intentos(self.sesion["id_sesion"])

        self.assertEqual(len(resultados), 3)
        self.assertEqual(len(intentos), 3)
        self.assertEqual(
            resultados[-1]["id_resultado"],
            tercero["id_resultado"],
        )
        self.assertEqual(
            intentos[-1]["id_resultado"],
            tercero["id_resultado"],
        )
        self.assertEqual(intentos[-1]["id_usuario"], self.id_usuario)
        self.assertEqual(intentos[-1]["id_letra"], self.id_letra_a)
        self.assertTrue(intentos[-1]["es_correcto"])
        self.assertEqual(self.leer_progreso(self.id_usuario), [])

        # El parche restauró el mínimo de tres definido en setUp.
        self.assertEqual(os.environ["APRENDIZAJE_MIN_ACIERTOS"], "3")

        # Un nuevo reconocimiento vuelve a evaluar los aciertos almacenados.
        cuarto = self.registrar_resultado()
        self.assertTrue(cuarto["es_correcto"])

        progreso = self.leer_progreso(self.id_usuario)
        self.assertEqual(len(progreso), 1)
        self.assertEqual(progreso[0]["id_usuario"], self.id_usuario)
        self.assertEqual(progreso[0]["id_letra"], self.id_letra_a)
        self.assertTrue(progreso[0]["dominada"])

        resultados_finales = self.leer_resultados(
            self.sesion["id_sesion"]
        )
        intentos_finales = self.leer_intentos(
            self.sesion["id_sesion"]
        )

        self.assertEqual(len(resultados_finales), 4)
        self.assertEqual(len(intentos_finales), 4)
        self.assertEqual(resultados_finales[:3], resultados)
        self.assertEqual(intentos_finales[:3], intentos)
        self.assertEqual(
            intentos_finales[-1]["id_resultado"],
            cuarto["id_resultado"],
        )


if __name__ == "__main__":
    unittest.main()
