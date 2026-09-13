import hashlib
import unittest
from unittest.mock import MagicMock, patch

from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

from app.routes.restablecimiento_contrasena import router
from app.services.autenticacion_service import autenticar_usuario
from app.services.restablecimiento_service import (
    SolicitudRecuperacionInvalidaError, restablecer_contrasena
)
from src.schemas.restablecimiento import SolicitudRestablecimiento


TOKEN = "A" * 43
CONTRASENA = "Nueva clave de prueba 2077!"


class TestRutaRestablecimiento(unittest.TestCase):
    def setUp(self):
        parche = patch("app.routes.restablecimiento_contrasena.restablecer_contrasena")
        self.restablecer = parche.start()
        self.addCleanup(parche.stop)
        aplicacion = FastAPI()
        autenticacion = APIRouter(prefix="/auth")
        autenticacion.include_router(router)
        aplicacion.include_router(autenticacion)
        self.cliente = TestClient(aplicacion)
        self.addCleanup(self.cliente.close)
        self.datos = {
            "token": TOKEN,
            "nueva_contrasena": CONTRASENA,
            "confirmacion_contrasena": CONTRASENA
        }

    def enviar(self, datos=None):
        return self.cliente.post(
            "/auth/restablecer-contrasena",
            json=self.datos if datos is None else datos
        )

    def test_actualiza_sin_login_y_no_devuelve_secretos(self):
        respuesta = self.enviar()
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(set(respuesta.json()), {"mensaje"})
        self.assertEqual(respuesta.headers["Cache-Control"], "no-store")
        self.assertNotIn(TOKEN, respuesta.text)
        self.assertNotIn(CONTRASENA, respuesta.text)
        self.restablecer.assert_called_once_with(TOKEN, CONTRASENA)

    def test_rechaza_confirmacion_diferente_sin_exponer_datos(self):
        self.datos["confirmacion_contrasena"] = "Otra clave de prueba!"
        respuesta = self.enviar()
        self.assertEqual(respuesta.status_code, 422)
        self.assertEqual(respuesta.json()["detail"], "Las contraseñas no coinciden.")
        for dato in self.datos.values():
            self.assertNotIn(dato, respuesta.text)
        self.restablecer.assert_not_called()

    def test_rechaza_longitud_y_tipo_de_contrasena(self):
        for valor in ("corta", "x" * 201, None, 123456789012, [CONTRASENA]):
            with self.subTest(tipo=type(valor).__name__):
                datos = dict(self.datos, nueva_contrasena=valor)
                respuesta = self.enviar(datos)
                self.assertEqual(respuesta.status_code, 422)
                self.assertNotIn(TOKEN, respuesta.text)
                self.assertNotIn(CONTRASENA, respuesta.text)
        self.restablecer.assert_not_called()

    def test_acepta_limites_de_longitud(self):
        for largo in (12, 200):
            with self.subTest(largo=largo):
                clave = "x" * largo
                respuesta = self.enviar(dict(
                    self.datos, nueva_contrasena=clave, confirmacion_contrasena=clave
                ))
                self.assertEqual(respuesta.status_code, 200)

    def test_conserva_espacios_y_unicode_en_contrasena(self):
        clave = "  Seña segura del usuario ñ!  "
        respuesta = self.enviar(dict(
            self.datos, nueva_contrasena=clave, confirmacion_contrasena=clave
        ))
        self.assertEqual(respuesta.status_code, 200)
        self.restablecer.assert_called_once_with(TOKEN, clave)

    def test_rechaza_token_mal_formado(self):
        for token in ("", "a" * 42, "a" * 44, "/" * 43, None, 123):
            with self.subTest(token=token):
                respuesta = self.enviar(dict(self.datos, token=token))
                self.assertEqual(respuesta.status_code, 422)
                self.assertEqual(respuesta.headers["Cache-Control"], "no-store")
        self.restablecer.assert_not_called()

    def test_rechaza_campos_ausentes_y_usuario_externo(self):
        for datos in ({}, dict(self.datos, id_usuario=999), {"token": TOKEN}):
            with self.subTest(campos=list(datos)):
                respuesta = self.enviar(datos)
                self.assertEqual(respuesta.status_code, 422)
                self.assertNotIn(TOKEN, respuesta.text)
        self.restablecer.assert_not_called()

    def test_json_mal_formado_no_devuelve_el_cuerpo(self):
        respuesta = self.cliente.post(
            "/auth/restablecer-contrasena",
            content='{"nueva_contrasena": "secreto-incompleto',
            headers={"Content-Type": "application/json"}
        )
        self.assertEqual(respuesta.status_code, 422)
        self.assertNotIn("secreto-incompleto", respuesta.text)
        self.restablecer.assert_not_called()

    def test_token_no_vigente_responde_400(self):
        self.restablecer.side_effect = SolicitudRecuperacionInvalidaError()
        respuesta = self.enviar()
        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(respuesta.headers["Cache-Control"], "no-store")
        self.assertNotIn(TOKEN, respuesta.text)

    def test_error_interno_no_expone_secretos_en_respuesta_o_log(self):
        self.restablecer.side_effect = RuntimeError(f"{TOKEN} {CONTRASENA}")
        with self.assertLogs("app.routes.restablecimiento_contrasena", level="ERROR") as logs:
            respuesta = self.enviar()
        self.assertEqual(respuesta.status_code, 500)
        self.assertEqual(respuesta.headers["Cache-Control"], "no-store")
        for secreto in (TOKEN, CONTRASENA):
            self.assertNotIn(secreto, respuesta.text)
            self.assertNotIn(secreto, " ".join(logs.output))

    def test_repr_del_modelo_oculta_secretos(self):
        modelo = SolicitudRestablecimiento(**self.datos)
        for secreto in (TOKEN, CONTRASENA):
            self.assertNotIn(secreto, repr(modelo))
            self.assertNotIn(secreto, modelo.model_dump_json())


class TestServicioRestablecimiento(unittest.TestCase):
    """Simula la conexión; la transacción real se verifica en PostgreSQL."""

    def setUp(self):
        self.conexion = MagicMock()
        self.conexion.__enter__.return_value = self.conexion
        self.conexion.__exit__.return_value = False
        self.cursor = MagicMock()
        self.conexion.cursor.return_value.__enter__.return_value = self.cursor
        parche = patch(
            "app.services.restablecimiento_service.obtener_conexion",
            return_value=self.conexion
        )
        parche.start()
        self.addCleanup(parche.stop)
        self.cursor.fetchone.side_effect = [
            {"id_recuperacion": 8, "id_usuario": 3},
            {"id_usuario": 3}, {"id_recuperacion": 8}, {"id_usuario": 3}
        ]

    def consultas(self):
        return [
            (" ".join(llamada.args[0].split()), llamada.args[1])
            for llamada in self.cursor.execute.call_args_list
        ]

    def test_actualiza_usuario_e_invalida_otras_solicitudes(self):
        with patch(
            "app.services.restablecimiento_service.generar_hash_contrasena",
            return_value="hash-de-prueba"
        ) as generar:
            restablecer_contrasena(TOKEN, CONTRASENA)
        generar.assert_called_once_with(CONTRASENA)
        consultas = self.consultas()
        self.assertEqual(consultas[3][1], ("hash-de-prueba", 3))
        self.assertIn("UPDATE usuarios", consultas[3][0])
        self.assertIn("SET fecha_invalidacion", consultas[4][0])
        self.assertIn("fecha_uso IS NULL", consultas[4][0])
        self.assertEqual(consultas[4][1], (3,))
        self.conexion.__exit__.assert_called_once_with(None, None, None)

    def test_hash_guardado_permite_login_nuevo_y_rechaza_anterior(self):
        restablecer_contrasena(TOKEN, CONTRASENA)
        consultas = self.consultas()
        hash_guardado = next(
            parametros[0] for sql, parametros in consultas
            if sql.startswith("UPDATE usuarios")
        )
        usuario = {
            "id_usuario": 3, "nombre": "Prueba", "correo": "prueba@example.com",
            "rol": "usuario", "contrasena_hash": hash_guardado
        }
        with patch(
            "app.services.autenticacion_service.obtener_usuario_por_correo",
            return_value=usuario
        ):
            self.assertEqual(autenticar_usuario(usuario["correo"], CONTRASENA)["id_usuario"], 3)
            self.assertIsNone(autenticar_usuario(usuario["correo"], "Clave anterior 2026!"))
        self.assertNotIn(CONTRASENA, repr(consultas))
        self.assertNotIn(TOKEN, repr(consultas))
        self.assertEqual(consultas[0][1], (hashlib.sha256(TOKEN.encode()).hexdigest(),))
        self.assertIn("FOR UPDATE", consultas[1][0])
        self.assertIn("fecha_uso IS NULL", consultas[-1][0])
        self.conexion.__exit__.assert_called_once_with(None, None, None)

    def test_solicitud_no_encontrada_no_cambia_contrasena(self):
        self.cursor.fetchone.side_effect = [None]
        with self.assertRaises(SolicitudRecuperacionInvalidaError):
            restablecer_contrasena(TOKEN, CONTRASENA)
        self.assertEqual(len(self.consultas()), 1)

    def test_consulta_excluye_tokens_vencidos_usados_e_invalidados(self):
        self.cursor.fetchone.side_effect = [None]
        with self.assertRaises(SolicitudRecuperacionInvalidaError):
            restablecer_contrasena(TOKEN, CONTRASENA)
        sql = self.consultas()[0][0]
        for condicion in (
            "fecha_uso IS NULL", "fecha_invalidacion IS NULL",
            "fecha_expiracion > statement_timestamp()"
        ):
            self.assertIn(condicion, sql)

    def test_usuario_eliminado_impide_actualizacion(self):
        self.cursor.fetchone.side_effect = [{"id_recuperacion": 8, "id_usuario": 3}, None]
        with self.assertRaises(SolicitudRecuperacionInvalidaError):
            restablecer_contrasena(TOKEN, CONTRASENA)
        self.assertFalse(any(sql.startswith("UPDATE") for sql, _ in self.consultas()))

    def test_token_que_deja_de_ser_valido_tras_bloqueo_no_cambia_clave(self):
        self.cursor.fetchone.side_effect = [
            {"id_recuperacion": 8, "id_usuario": 3}, {"id_usuario": 3}, None
        ]
        with self.assertRaises(SolicitudRecuperacionInvalidaError) as error:
            restablecer_contrasena(TOKEN, CONTRASENA)
        consultas = self.consultas()
        self.assertFalse(any(sql.startswith("UPDATE usuarios") for sql, _ in consultas))
        for condicion in (
            "fecha_uso IS NULL", "fecha_invalidacion IS NULL",
            "fecha_expiracion > statement_timestamp()"
        ):
            self.assertIn(condicion, consultas[-1][0])
        self.assertIs(self.conexion.__exit__.call_args.args[1], error.exception)

    def test_fallo_al_guardar_sale_de_transaccion_con_error(self):
        error = RuntimeError("Fallo de escritura simulado")
        self.cursor.execute.side_effect = [None, None, None, error]
        with self.assertRaises(RuntimeError):
            restablecer_contrasena(TOKEN, CONTRASENA)
        self.assertIs(self.conexion.__exit__.call_args.args[1], error)

    def test_fallo_al_confirmar_transaccion_no_se_oculta(self):
        self.conexion.__exit__.side_effect = RuntimeError("Fallo de commit simulado")
        with self.assertRaisesRegex(RuntimeError, "Fallo de commit"):
            restablecer_contrasena(TOKEN, CONTRASENA)


if __name__ == "__main__":
    unittest.main()
