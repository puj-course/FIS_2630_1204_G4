import os
import smtplib
import ssl
import unittest
from dataclasses import replace
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs, urlsplit

from app.services.correo_recuperacion_service import (
    ConfiguracionCorreoError,
    enviar_correo_recuperacion,
    obtener_configuracion_correo
)


class TestConfiguracionCorreoRecuperacion(unittest.TestCase):
    def setUp(self):
        self.entorno = {
            "SMTP_HOST": "smtp.example.com",
            "SMTP_PORT": "587",
            "SMTP_SECURITY": "starttls",
            "SMTP_USER": "cuenta@example.com",
            "SMTP_PASSWORD": "clave-smtp-exclusiva-de-prueba",
            "SMTP_FROM": "signia@example.com",
            "RECUPERACION_URL": "https://signia.example.com/restablecer-contrasena"
        }
        parche = patch.dict(os.environ, self.entorno, clear=True)
        parche.start()
        self.addCleanup(parche.stop)

    def test_acepta_configuracion_completa(self):
        configuracion = obtener_configuracion_correo()

        self.assertEqual(configuracion.host, "smtp.example.com")
        self.assertEqual(configuracion.puerto, 587)
        self.assertEqual(configuracion.seguridad, "starttls")

    def test_rechaza_variables_obligatorias_vacias(self):
        for nombre in (
            "SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM",
            "RECUPERACION_URL"
        ):
            with self.subTest(variable=nombre):
                with patch.dict(os.environ, {nombre: ""}):
                    with self.assertRaises(ConfiguracionCorreoError):
                        obtener_configuracion_correo()

    def test_rechaza_puertos_invalidos(self):
        for puerto in ("abc", "", "0", "-1", "65536"):
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

    def test_acepta_tls_desde_el_inicio(self):
        with patch.dict(os.environ, {"SMTP_SECURITY": "ssl", "SMTP_PORT": "465"}):
            configuracion = obtener_configuracion_correo()

        self.assertEqual(configuracion.seguridad, "ssl")
        self.assertEqual(configuracion.puerto, 465)

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
        self.assertNotIn(configuracion.contrasena, repr(configuracion))


class TestEnvioCorreoRecuperacion(unittest.TestCase):
    def setUp(self):
        from app.services.correo_recuperacion_service import ConfiguracionCorreo

        self.configuracion = ConfiguracionCorreo(
            host="smtp.example.com",
            puerto=587,
            seguridad="starttls",
            usuario="cuenta@example.com",
            contrasena="clave-smtp-exclusiva-de-prueba",
            remitente="signia@example.com",
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
        parche_ssl = patch(
            "app.services.correo_recuperacion_service.smtplib.SMTP_SSL",
            return_value=self.servidor
        )
        self.smtp_ssl = parche_ssl.start()
        self.addCleanup(parche_ssl.stop)

    def enviar(self, configuracion=None):
        enviar_correo_recuperacion(
            "persona@example.com",
            "token-exclusivo-de-prueba",
            self.fecha,
            configuracion or self.configuracion
        )

    def test_cifra_antes_de_autenticar_y_enviar(self):
        self.enviar()

        operaciones = [llamada[0] for llamada in self.servidor.method_calls]
        self.assertEqual(
            operaciones,
            ["ehlo", "starttls", "ehlo", "login", "send_message"]
        )
        contexto = self.servidor.starttls.call_args.kwargs["context"]
        self.assertTrue(contexto.check_hostname)
        self.assertEqual(contexto.verify_mode, ssl.CERT_REQUIRED)
        self.smtp.assert_called_once_with("smtp.example.com", 587, timeout=10)
        self.smtp_ssl.assert_not_called()

    def test_no_envia_credenciales_si_falla_tls(self):
        self.servidor.starttls.side_effect = smtplib.SMTPNotSupportedError(
            "TLS no disponible"
        )

        with self.assertRaises(smtplib.SMTPNotSupportedError):
            self.enviar()

        self.servidor.login.assert_not_called()
        self.servidor.send_message.assert_not_called()

    def test_utiliza_tls_desde_inicio_cuando_se_configura(self):
        self.enviar(replace(self.configuracion, seguridad="ssl", puerto=465))

        self.smtp.assert_not_called()
        self.smtp_ssl.assert_called_once()
        self.assertEqual(self.smtp_ssl.call_args.args, ("smtp.example.com", 465))
        contexto = self.smtp_ssl.call_args.kwargs["context"]
        self.assertTrue(contexto.check_hostname)
        self.assertEqual(contexto.verify_mode, ssl.CERT_REQUIRED)
        self.servidor.starttls.assert_not_called()
        self.servidor.login.assert_called_once()

    def test_envia_enlace_y_vencimiento_solo_al_destinatario(self):
        self.enviar()

        llamada = self.servidor.send_message.call_args
        mensaje = llamada.args[0]
        self.assertEqual(str(mensaje["To"]), "persona@example.com")
        self.assertEqual(llamada.kwargs["to_addrs"], ["persona@example.com"])
        self.assertEqual(llamada.kwargs["from_addr"], "signia@example.com")
        self.assertIsNone(mensaje["Cc"])
        self.assertIsNone(mensaje["Bcc"])
        contenido = mensaje.get_content()
        self.assertIn("2026-01-01 12:15 UTC", contenido)
        self.assertNotIn(self.configuracion.contrasena, contenido)
        enlace = next(linea for linea in contenido.splitlines() if linea.startswith("https://"))
        partes = urlsplit(enlace)
        self.assertEqual(partes.netloc, "signia.example.com")
        self.assertEqual(partes.query, "")
        self.assertEqual(
            parse_qs(partes.fragment),
            {"token": ["token-exclusivo-de-prueba"]}
        )

    def test_no_envia_si_falla_autenticacion_smtp(self):
        self.servidor.login.side_effect = smtplib.SMTPAuthenticationError(
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
