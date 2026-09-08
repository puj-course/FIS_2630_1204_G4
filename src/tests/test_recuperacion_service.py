import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from psycopg.rows import dict_row

from app.services.recuperacion_service import (
    crear_solicitud_recuperacion,
    generar_hash_token
)


class TestHashTokenRecuperacion(unittest.TestCase):
    def test_utiliza_sha256(self):
        self.assertEqual(
            generar_hash_token("abc"),
            "ba7816bf8f01cfea414140de5dae2223"
            "b00361a396177a9cb410ff61f20015ad"
        )

    def test_genera_64_caracteres_hexadecimales(self):
        self.assertRegex(generar_hash_token("token-de-prueba"), r"^[0-9a-f]{64}$")

    def test_tokens_distintos_producen_hashes_distintos(self):
        self.assertNotEqual(
            generar_hash_token("token-uno"),
            generar_hash_token("token-dos")
        )


class TestCrearSolicitudRecuperacion(unittest.TestCase):
    def setUp(self):
        parche_conexion = patch(
            "app.services.recuperacion_service.obtener_conexion"
        )
        self.obtener_conexion = parche_conexion.start()
        self.addCleanup(parche_conexion.stop)

        self.conexion = MagicMock()
        self.conexion.__enter__.return_value = self.conexion
        self.conexion.__exit__.return_value = False
        self.obtener_conexion.return_value = self.conexion

        self.cursor = MagicMock()
        self.cursor.__enter__.return_value = self.cursor
        self.cursor.__exit__.return_value = False
        self.conexion.cursor.return_value = self.cursor

        parche_token = patch(
            "app.services.recuperacion_service.secrets.token_urlsafe",
            return_value="token-exclusivo-de-prueba"
        )
        self.generar_token = parche_token.start()
        self.addCleanup(parche_token.stop)

        self.usuario = {
            "id_usuario": 7,
            "correo": "persona@example.com"
        }
        self.solicitud = {
            "id_recuperacion": 20,
            "fecha_expiracion": datetime(2026, 1, 1, 12, 15, tzinfo=timezone.utc)
        }
        self.cursor.fetchone.side_effect = [self.usuario, None, self.solicitud]

    def consulta(self, indice):
        llamada = self.cursor.execute.call_args_list[indice]
        return " ".join(llamada.args[0].split()), llamada.args[1]

    def test_crea_solicitud_para_usuario_registrado(self):
        resultado = crear_solicitud_recuperacion("persona@example.com")

        self.assertEqual(resultado.id_recuperacion, 20)
        self.assertEqual(resultado.correo, "persona@example.com")
        self.assertEqual(resultado.token, "token-exclusivo-de-prueba")
        self.assertEqual(
            resultado.fecha_expiracion,
            self.solicitud["fecha_expiracion"]
        )
        self.conexion.__exit__.assert_called_once_with(None, None, None)

    def test_normaliza_correo_y_utiliza_parametros_sql(self):
        crear_solicitud_recuperacion("  Persona@Example.COM  ")

        sql, parametros = self.consulta(0)
        self.assertIn("WHERE LOWER(correo) = LOWER(%s)", sql)
        self.assertEqual(parametros, ("persona@example.com",))
        self.assertNotIn("persona@example.com", sql)

    def test_no_crea_solicitud_para_usuario_inexistente(self):
        self.cursor.fetchone.side_effect = [None]

        self.assertIsNone(crear_solicitud_recuperacion("nadie@example.com"))

        self.assertEqual(self.cursor.execute.call_count, 1)
        self.generar_token.assert_not_called()

    def test_no_crea_otra_solicitud_durante_intervalo_minimo(self):
        self.cursor.fetchone.side_effect = [self.usuario, {"id_recuperacion": 19}]

        self.assertIsNone(crear_solicitud_recuperacion("persona@example.com"))

        self.assertEqual(self.cursor.execute.call_count, 2)
        self.generar_token.assert_not_called()

    def test_consulta_intervalo_de_60_segundos(self):
        crear_solicitud_recuperacion("persona@example.com")

        sql, parametros = self.consulta(1)
        self.assertIn("fecha_creacion > statement_timestamp() - %s", sql)
        self.assertEqual(parametros, (7, timedelta(seconds=60)))

    def test_genera_token_con_32_bytes_aleatorios(self):
        crear_solicitud_recuperacion("persona@example.com")

        self.generar_token.assert_called_once_with(32)

    def test_guarda_hash_y_no_token_original(self):
        crear_solicitud_recuperacion("persona@example.com")

        sql, parametros = self.consulta(3)
        self.assertIn("INSERT INTO recuperaciones_contrasena", sql)
        self.assertEqual(parametros[0], 7)
        self.assertEqual(
            parametros[1],
            generar_hash_token("token-exclusivo-de-prueba")
        )
        for llamada in self.cursor.execute.call_args_list:
            self.assertNotIn("token-exclusivo-de-prueba", repr(llamada))

    def test_define_expiracion_de_15_minutos_con_hora_de_base_de_datos(self):
        crear_solicitud_recuperacion("persona@example.com")

        sql, parametros = self.consulta(3)
        self.assertIn("statement_timestamp(), statement_timestamp() + %s", sql)
        self.assertEqual(parametros[2], timedelta(minutes=15))

    def test_bloquea_usuario_y_usa_una_sola_conexion(self):
        crear_solicitud_recuperacion("persona@example.com")

        sql, _ = self.consulta(0)
        self.assertIn("FOR UPDATE", sql)
        self.obtener_conexion.assert_called_once_with()
        self.conexion.cursor.assert_called_once_with(row_factory=dict_row)
        self.assertEqual(self.cursor.execute.call_count, 4)

    def test_invalida_solo_solicitudes_pendientes_del_usuario(self):
        crear_solicitud_recuperacion("persona@example.com")

        sql, parametros = self.consulta(2)
        self.assertIn("UPDATE recuperaciones_contrasena", sql)
        self.assertIn("SET fecha_invalidacion = statement_timestamp()", sql)
        self.assertIn("WHERE id_usuario = %s", sql)
        self.assertIn("fecha_uso IS NULL", sql)
        self.assertIn("fecha_invalidacion IS NULL", sql)
        self.assertIn("fecha_expiracion > statement_timestamp()", sql)
        self.assertEqual(parametros, (7,))

    def test_propaga_error_al_consultar_usuario(self):
        error = RuntimeError("Error simulado de consulta")
        self.cursor.execute.side_effect = error

        with self.assertRaisesRegex(RuntimeError, "Error simulado de consulta"):
            crear_solicitud_recuperacion("persona@example.com")

        self.generar_token.assert_not_called()
        self.assertIs(self.conexion.__exit__.call_args.args[1], error)

    def test_error_de_insercion_sale_del_contexto_con_excepcion(self):
        error = RuntimeError("Error simulado de inserción")
        self.cursor.execute.side_effect = [None, None, None, error]

        with self.assertRaisesRegex(RuntimeError, "Error simulado de inserción"):
            crear_solicitud_recuperacion("persona@example.com")

        self.assertIs(self.conexion.__exit__.call_args.args[1], error)

    def test_no_devuelve_token_si_falla_confirmacion_de_transaccion(self):
        self.conexion.__exit__.side_effect = RuntimeError("Error simulado de commit")

        with self.assertRaisesRegex(RuntimeError, "Error simulado de commit"):
            crear_solicitud_recuperacion("persona@example.com")

    def test_rechaza_insercion_sin_resultado(self):
        self.cursor.fetchone.side_effect = [self.usuario, None, None]

        with self.assertRaisesRegex(RuntimeError, "No fue posible crear la solicitud"):
            crear_solicitud_recuperacion("persona@example.com")

        self.assertIs(self.conexion.__exit__.call_args.args[0], RuntimeError)

    def test_representacion_no_muestra_token_ni_correo(self):
        resultado = crear_solicitud_recuperacion("persona@example.com")

        self.assertNotIn(resultado.token, repr(resultado))
        self.assertNotIn(resultado.correo, repr(resultado))


if __name__ == "__main__":
    unittest.main()
