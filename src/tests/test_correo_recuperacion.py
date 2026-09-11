import os
import smtplib
import ssl
import unittest

import httpx
from dataclasses import replace
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs, urlsplit

from app.services.correo_recuperacion_service import (
    ConfiguracionCorreoError,
    EnvioMicrosoftGraphError,
    enviar_correo_recuperacion,
    obtener_configuracion_correo
)


class TestConfiguracionCorreoRecuperacion(unittest.TestCase):
    def setUp(self):
        self.entorno = {
            "SMTP_HOST": "smtp-mail.outlook.com",
            "SMTP_PORT": "587",
            "SMTP_SECURITY": "starttls",
            "SMTP_USER": "cuenta@example.com",
            "MICROSOFT_CLIENT_ID": "11111111-2222-4333-8444-555555555555",
            "SMTP_FROM": "cuenta@example.com",
            "RECUPERACION_URL": "https://signia.example.com/restablecer-contrasena"
        }
        parche = patch.dict(os.environ, self.entorno, clear=True)
        parche.start()
        self.addCleanup(parche.stop)

    def test_graph_no_requiere_servidor_smtp(self):
        with patch.dict(os.environ, {
            "CORREO_TRANSPORTE": "graph", "SMTP_HOST": "",
            "SMTP_PORT": "", "SMTP_SECURITY": ""
        }):
            self.assertEqual(obtener_configuracion_correo().transporte, "graph")

    def test_rechaza_transporte_desconocido(self):
        with patch.dict(os.environ, {"CORREO_TRANSPORTE": "otro"}):
            with self.assertRaises(ConfiguracionCorreoError):
                obtener_configuracion_correo()

    def test_acepta_configuracion_completa(self):
        configuracion = obtener_configuracion_correo()

        self.assertEqual(configuracion.host, "smtp-mail.outlook.com")
        self.assertEqual(configuracion.puerto, 587)
        self.assertEqual(configuracion.seguridad, "starttls")

    def test_rechaza_variables_obligatorias_vacias(self):
        for nombre in (
            "SMTP_HOST", "SMTP_USER", "MICROSOFT_CLIENT_ID", "SMTP_FROM",
            "RECUPERACION_URL"
        ):
            with self.subTest(variable=nombre):
                with patch.dict(os.environ, {nombre: ""}):
                    with self.assertRaises(ConfiguracionCorreoError):
                        obtener_configuracion_correo()

    def test_rechaza_puertos_invalidos(self):
        for puerto in ("abc", "", "0", "-1", "65536", "465", "25"):
            with self.subTest(puerto=puerto):
                with patch.dict(os.environ, {"SMTP_PORT": puerto}):
                    with self.assertRaises(ConfiguracionCorreoError):
                        obtener_configuracion_correo()

    def test_rechaza_correo_remitente_invalido(self):
        with patch.dict(os.environ, {"SMTP_FROM": "correo-invalido"}):
            with self.assertRaises(ConfiguracionCorreoError):
                obtener_configuracion_correo()

    def test_rechaza_smtp_sin_cifrado(self):
        with patch.dict(os.environ, {"SMTP_SECURITY": "none"}):
            with self.assertRaises(ConfiguracionCorreoError):
                obtener_configuracion_correo()

    def test_rechaza_ssl_465_para_outlook_personal(self):
        with patch.dict(os.environ, {"SMTP_SECURITY": "ssl", "SMTP_PORT": "465"}):
            with self.assertRaises(ConfiguracionCorreoError):
                obtener_configuracion_correo()

    def test_rechaza_configuracion_de_otra_cuenta_o_servidor(self):
        for cambios in (
            {"SMTP_FROM": "otra@example.com"},
            {"SMTP_HOST": "smtp.example.com"},
            {"MICROSOFT_CLIENT_ID": "no-es-un-id"},
            {"SMTP_USER": "correo-invalido"}
        ):
            with self.subTest(cambios=cambios), patch.dict(os.environ, cambios):
                with self.assertRaises(ConfiguracionCorreoError):
                    obtener_configuracion_correo()

    def test_no_requiere_contrasena_de_hotmail(self):
        with patch.dict(os.environ, {"SMTP_PASSWORD": ""}):
            configuracion = obtener_configuracion_correo()
        self.assertFalse(hasattr(configuracion, "contrasena"))

    def test_permite_http_para_desarrollo_local(self):
        for host in ("localhost", "127.0.0.1", "[::1]"):
            url = f"http://{host}:5173/restablecer-contrasena"
            with self.subTest(url=url):
                with patch.dict(os.environ, {"RECUPERACION_URL": url}):
                    self.assertEqual(
                        obtener_configuracion_correo().url_recuperacion,
                        url
                    )

    def test_rechaza_urls_inseguras_o_ambiguas(self):
        urls = (
            "http://signia.example.com/restablecer",
            "javascript:alert(1)",
            "/restablecer",
            "https://",
            "https://usuario:clave@example.com/restablecer",
            "https://example.com/restablecer?token=anterior",
            "https://example.com/restablecer#token=anterior",
            "https://example.com:abc/restablecer",
            "https://example.com:0/restablecer",
            "https://example.com/restablecer\ncontrasena"
        )
        for url in urls:
            with self.subTest(url=url):
                with patch.dict(os.environ, {"RECUPERACION_URL": url}):
                    with self.assertRaises(ConfiguracionCorreoError):
                        obtener_configuracion_correo()

    def test_representacion_no_muestra_credenciales(self):
        configuracion = obtener_configuracion_correo()

        self.assertNotIn(configuracion.usuario, repr(configuracion))
        self.assertNotIn(configuracion.remitente, repr(configuracion))


class TestEnvioCorreoRecuperacion(unittest.TestCase):
    def setUp(self):
        from app.services.correo_recuperacion_service import ConfiguracionCorreo

        self.configuracion = ConfiguracionCorreo(
            host="smtp-mail.outlook.com",
            puerto=587,
            seguridad="starttls",
            usuario="cuenta@example.com",
            client_id="11111111-2222-4333-8444-555555555555",
            remitente="cuenta@example.com",
            url_recuperacion="https://signia.example.com/restablecer-contrasena"
        )
        self.fecha = datetime(2026, 1, 1, 12, 15, tzinfo=timezone.utc)
        self.servidor = MagicMock()
        self.servidor.__enter__.return_value = self.servidor
        self.servidor.__exit__.return_value = False
        self.servidor.send_message.return_value = {}

        parche_smtp = patch(
            "app.services.correo_recuperacion_service.smtplib.SMTP",
            return_value=self.servidor
        )
        self.smtp = parche_smtp.start()
        self.addCleanup(parche_smtp.stop)
        self.token_microsoft = "access-token-microsoft-de-prueba"
        parche_token = patch(
            "app.services.correo_recuperacion_service.obtener_token_microsoft",
            return_value=self.token_microsoft
        )
        self.obtener_token = parche_token.start()
        self.addCleanup(parche_token.stop)

    def enviar(self, configuracion=None):
        enviar_correo_recuperacion(
            "persona@example.com",
            "token-exclusivo-de-prueba",
            self.fecha,
            configuracion or self.configuracion
        )

    def test_graph_envia_enlace_al_destinatario_con_token_de_graph(self):
        with patch("app.services.correo_recuperacion_service.httpx.post") as enviar:
            enviar.return_value.status_code = 202
            self.enviar(replace(self.configuracion, transporte="graph"))
        self.smtp.assert_not_called()
        self.obtener_token.assert_called_once_with(
            self.configuracion.client_id, self.configuracion.usuario, transporte="graph"
        )
        self.assertEqual(enviar.call_count, 1)
        llamada = enviar.call_args
        self.assertEqual(llamada.args, ("https://graph.microsoft.com/v1.0/me/sendMail",))
        self.assertEqual(llamada.kwargs["headers"], {
            "Authorization": f"Bearer {self.token_microsoft}"
        })
        self.assertFalse(llamada.kwargs["follow_redirects"])
        self.assertEqual(llamada.kwargs["timeout"], 10)
        self.assertNotEqual(llamada.kwargs.get("verify"), False)
        mensaje = llamada.kwargs["json"]["message"]
        self.assertEqual(mensaje["toRecipients"], [
            {"emailAddress": {"address": "persona@example.com"}}
        ])
        self.assertEqual(set(mensaje), {"subject", "body", "toRecipients"})
        self.assertEqual(mensaje["body"]["contentType"], "Text")
        self.assertIn("#token=token-exclusivo-de-prueba", mensaje["body"]["content"])
        self.assertIn("2026-01-01 12:15 UTC", mensaje["body"]["content"])
        self.assertNotIn(self.token_microsoft, str(mensaje))

    def test_graph_rechazos_no_reintentan_ni_usan_smtp(self):
        for estado in (301, 401, 403, 429, 500):
            with self.subTest(estado=estado):
                with patch("app.services.correo_recuperacion_service.httpx.post") as enviar:
                    enviar.return_value.status_code = estado
                    enviar.return_value.text = "detalle-privado"
                    with self.assertRaises(EnvioMicrosoftGraphError) as error:
                        self.enviar(replace(self.configuracion, transporte="graph"))
                    self.assertIn(str(estado), str(error.exception))
                    self.assertNotIn("detalle-privado", str(error.exception))
                    enviar.assert_called_once()
        self.smtp.assert_not_called()

    def test_graph_error_de_red_no_expone_tokens_ni_reintenta(self):
        with patch("app.services.correo_recuperacion_service.httpx.post") as enviar:
            enviar.side_effect = httpx.ConnectError(self.token_microsoft)
            with self.assertRaises(EnvioMicrosoftGraphError) as error:
                self.enviar(replace(self.configuracion, transporte="graph"))
            self.assertNotIn(self.token_microsoft, str(error.exception))
            enviar.assert_called_once()
        self.smtp.assert_not_called()

    def test_graph_sin_autorizacion_no_envia(self):
        self.obtener_token.side_effect = RuntimeError("Autorización pendiente")
        with patch("app.services.correo_recuperacion_service.httpx.post") as enviar:
            with self.assertRaises(RuntimeError):
                self.enviar(replace(self.configuracion, transporte="graph"))
            enviar.assert_not_called()
        self.smtp.assert_not_called()

    def test_cifra_antes_de_autenticar_y_enviar(self):
        self.enviar()

        operaciones = [llamada[0] for llamada in self.servidor.method_calls]
        self.assertEqual(
            operaciones,
            ["ehlo", "starttls", "ehlo", "auth", "send_message"]
        )
        contexto = self.servidor.starttls.call_args.kwargs["context"]
        self.assertTrue(contexto.check_hostname)
        self.assertEqual(contexto.verify_mode, ssl.CERT_REQUIRED)
        self.smtp.assert_called_once_with("smtp-mail.outlook.com", 587, timeout=10)
        self.servidor.login.assert_not_called()
        self.obtener_token.assert_called_once_with(
            self.configuracion.client_id, self.configuracion.usuario
        )
        mecanismo, respuesta = self.servidor.auth.call_args.args
        self.assertEqual(mecanismo, "XOAUTH2")
        self.assertEqual(
            respuesta(),
            f"user=cuenta@example.com\x01auth=Bearer {self.token_microsoft}\x01\x01"
        )
        self.assertEqual(respuesta(b"error del servidor"), "")

    def test_no_envia_credenciales_si_falla_tls(self):
        self.servidor.starttls.side_effect = smtplib.SMTPNotSupportedError(
            "TLS no disponible"
        )

        with self.assertRaises(smtplib.SMTPNotSupportedError):
            self.enviar()

        self.servidor.auth.assert_not_called()
        self.servidor.send_message.assert_not_called()

    def test_no_envia_token_a_otro_servidor(self):
        with self.assertRaises(ConfiguracionCorreoError):
            self.enviar(replace(self.configuracion, host="otro.example.com"))

        self.smtp.assert_not_called()
        self.obtener_token.assert_not_called()

    def test_no_conecta_smtp_sin_autorizacion_microsoft(self):
        self.obtener_token.side_effect = RuntimeError("Autorización pendiente")
        with self.assertRaises(RuntimeError):
            self.enviar()
        self.smtp.assert_not_called()

    def test_envia_enlace_y_vencimiento_solo_al_destinatario(self):
        self.enviar()

        llamada = self.servidor.send_message.call_args
        mensaje = llamada.args[0]
        self.assertEqual(str(mensaje["To"]), "persona@example.com")
        self.assertEqual(llamada.kwargs["to_addrs"], ["persona@example.com"])
        self.assertEqual(llamada.kwargs["from_addr"], "cuenta@example.com")
        self.assertIsNone(mensaje["Cc"])
        self.assertIsNone(mensaje["Bcc"])
        contenido = mensaje.get_content()
        self.assertIn("2026-01-01 12:15 UTC", contenido)
        self.assertNotIn(self.token_microsoft, mensaje.as_string())
        enlace = next(linea for linea in contenido.splitlines() if linea.startswith("https://"))
        partes = urlsplit(enlace)
        self.assertEqual(partes.netloc, "signia.example.com")
        self.assertEqual(partes.query, "")
        self.assertEqual(
            parse_qs(partes.fragment),
            {"token": ["token-exclusivo-de-prueba"]}
        )

    def test_no_envia_si_falla_autenticacion_smtp(self):
        self.servidor.auth.side_effect = smtplib.SMTPAuthenticationError(
            535, b"Error simulado"
        )

        with self.assertRaises(smtplib.SMTPAuthenticationError):
            self.enviar()

        self.servidor.send_message.assert_not_called()

    def test_propaga_rechazo_del_destinatario(self):
        self.servidor.send_message.return_value = {
            "persona@example.com": (550, b"Rechazo simulado")
        }

        with self.assertRaises(smtplib.SMTPRecipientsRefused):
            self.enviar()


if __name__ == "__main__":
    unittest.main()
