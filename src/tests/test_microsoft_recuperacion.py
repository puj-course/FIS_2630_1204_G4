import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

from app.services import microsoft_oauth_service as oauth


CLIENT_ID = "11111111-2222-4333-8444-555555555555"
CORREO = "remitente@hotmail.com"


class TestPersistenciaMicrosoft(unittest.TestCase):
    def setUp(self):
        temporal = TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.carpeta = Path(temporal.name)
        parche = patch.object(oauth.Path, "home", return_value=self.carpeta)
        parche.start()
        self.addCleanup(parche.stop)

    def test_separa_cache_por_aplicacion_y_cuenta_fuera_del_proyecto(self):
        with patch.object(oauth, "build_encrypted_persistence") as construir:
            construir.return_value.is_encrypted = True
            oauth.crear_persistencia_microsoft(CLIENT_ID, CORREO)
            oauth.crear_persistencia_microsoft(CLIENT_ID, "otra@hotmail.com")
            oauth.crear_persistencia_microsoft(
                "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee", CORREO
            )
        rutas = [Path(llamada.args[0]) for llamada in construir.call_args_list]
        self.assertEqual(len(set(rutas)), 3)
        for ruta in rutas:
            self.assertTrue(ruta.is_relative_to(self.carpeta / ".signia"))
            self.assertNotIn(CORREO, str(ruta))

    def test_graph_tiene_cache_distinta_de_smtp(self):
        with patch.object(oauth, "build_encrypted_persistence") as construir:
            construir.return_value.is_encrypted = True
            oauth.crear_persistencia_microsoft(CLIENT_ID, CORREO)
            oauth.crear_persistencia_microsoft(CLIENT_ID, CORREO, "graph")
        rutas = [Path(llamada.args[0]) for llamada in construir.call_args_list]
        self.assertNotEqual(rutas[0], rutas[1])
        self.assertEqual(rutas[1].parent, rutas[0].parent / "graph")

    def test_rechaza_almacenamiento_sin_cifrado(self):
        with patch.object(oauth, "build_encrypted_persistence") as construir:
            construir.return_value.is_encrypted = False
            with self.assertRaises(oauth.AutorizacionMicrosoftError):
                oauth.crear_persistencia_microsoft(CLIENT_ID, CORREO)

    def test_falla_con_mensaje_del_sistema_sin_exponer_detalles(self):
        for sistema, ayuda in (("linux", "libsecret"), ("win32", "DPAPI"), ("darwin", "Keychain")):
            with self.subTest(sistema=sistema), patch.object(oauth.sys, "platform", sistema):
                with patch.object(
                    oauth, "build_encrypted_persistence",
                    side_effect=RuntimeError("detalle-privado")
                ):
                    with self.assertRaisesRegex(oauth.AutorizacionMicrosoftError, ayuda) as error:
                        oauth.crear_persistencia_microsoft(CLIENT_ID, CORREO)
                self.assertNotIn("detalle-privado", str(error.exception))


class TestAutorizacionMicrosoft(unittest.TestCase):
    def setUp(self):
        self.persistencia = MagicMock()
        self.persistencia.get_location.return_value = "/cache/prueba.bin"
        self.aplicacion = MagicMock()
        self.cuenta = {"username": CORREO, "home_account_id": "cuenta-de-prueba"}
        self.aplicacion.get_accounts.return_value = [self.cuenta]
        self.aplicacion.acquire_token_silent.return_value = {
            "access_token": "access-token-de-prueba"
        }
        self.aplicacion.initiate_device_flow.return_value = {
            "user_code": "CODIGO-PRUEBA", "device_code": "device-code-privado",
            "verification_uri": "https://www.microsoft.com/link"
        }
        self.aplicacion.acquire_token_by_device_flow.return_value = {
            "access_token": "access-token-de-prueba",
            "refresh_token": "refresh-token-de-prueba"
        }
        for nombre, resultado in (
            ("crear_persistencia_microsoft", self.persistencia),
            ("crear_aplicacion_microsoft", self.aplicacion),
            ("PersistedTokenCache", MagicMock()),
            ("CrossPlatLock", MagicMock())
        ):
            parche = patch.object(oauth, nombre, return_value=resultado)
            parche.start()
            self.addCleanup(parche.stop)

    def test_graph_autoriza_y_renueva_con_permiso_mail_send(self):
        oauth.autorizar_cuenta_microsoft(
            CLIENT_ID, CORREO, mostrar=lambda _: None, transporte="graph"
        )
        self.aplicacion.initiate_device_flow.assert_called_once_with(
            scopes=["https://graph.microsoft.com/Mail.Send"]
        )
        oauth.obtener_token_microsoft(CLIENT_ID, CORREO, transporte="graph")
        self.aplicacion.acquire_token_silent.assert_called_once_with(
            scopes=["https://graph.microsoft.com/Mail.Send"], account=self.cuenta
        )
        oauth.crear_persistencia_microsoft.assert_called_with(CLIENT_ID, CORREO, "graph")

    def test_renueva_token_para_la_cuenta_remitente(self):
        token = oauth.obtener_token_microsoft(CLIENT_ID, " Remitente@Hotmail.COM ")
        self.assertEqual(token, "access-token-de-prueba")
        self.aplicacion.get_accounts.assert_called_once_with(username=CORREO)
        self.aplicacion.acquire_token_silent.assert_called_once_with(
            scopes=["https://outlook.office.com/SMTP.Send"], account=self.cuenta
        )
        self.aplicacion.initiate_device_flow.assert_not_called()

    def test_no_elije_otra_cuenta_ni_inicia_login_desde_el_backend(self):
        for cuentas in ([], [self.cuenta, self.cuenta]):
            with self.subTest(cuentas=cuentas):
                self.aplicacion.get_accounts.return_value = cuentas
                with self.assertRaises(oauth.AutorizacionMicrosoftError):
                    oauth.obtener_token_microsoft(CLIENT_ID, CORREO)
        self.aplicacion.acquire_token_silent.assert_not_called()
        self.aplicacion.initiate_device_flow.assert_not_called()

    def test_revocacion_o_expiracion_exige_nueva_autorizacion(self):
        for resultado in (None, {}, {"error": "invalid_grant"}, {"access_token": ""}):
            with self.subTest(resultado=resultado):
                self.aplicacion.acquire_token_silent.return_value = resultado
                with self.assertRaisesRegex(oauth.AutorizacionMicrosoftError, "otra vez"):
                    oauth.obtener_token_microsoft(CLIENT_ID, CORREO)
        self.aplicacion.initiate_device_flow.assert_not_called()

    def test_autorizacion_guarda_cache_sin_imprimir_tokens(self):
        mensajes = []
        oauth.autorizar_cuenta_microsoft(CLIENT_ID, CORREO, mostrar=mensajes.append)
        self.aplicacion.initiate_device_flow.assert_called_once_with(
            scopes=["https://outlook.office.com/SMTP.Send"]
        )
        self.persistencia.save.assert_called_once()
        salida = "\n".join(mensajes)
        self.assertIn("CODIGO-PRUEBA", salida)
        self.assertIn("https://www.microsoft.com/link", salida)
        self.assertNotIn("https://microsoft.com/devicelogin", salida)
        for secreto in ("access-token-de-prueba", "refresh-token-de-prueba", "device-code-privado"):
            self.assertNotIn(secreto, salida)

    def test_autorizacion_de_cuenta_distinta_no_se_guarda(self):
        self.aplicacion.get_accounts.return_value = []
        with self.assertRaisesRegex(oauth.AutorizacionMicrosoftError, "no coincide"):
            oauth.autorizar_cuenta_microsoft(CLIENT_ID, CORREO, mostrar=lambda _: None)
        self.persistencia.save.assert_not_called()

    def test_permiso_denegado_no_se_guarda_ni_expone_detalle_privado(self):
        self.aplicacion.acquire_token_by_device_flow.return_value = {
            "error": "access_denied", "error_description": "detalle-privado",
            "error_codes": [65001]
        }
        with self.assertRaises(oauth.AutorizacionMicrosoftError) as resultado:
            oauth.autorizar_cuenta_microsoft(CLIENT_ID, CORREO, mostrar=lambda _: None)
        self.assertIn("65001", str(resultado.exception))
        self.assertNotIn("detalle-privado", str(resultado.exception))
        self.persistencia.save.assert_not_called()

    def test_flujo_no_disponible_no_espera_ni_guarda(self):
        for flujo in ({"error": "unauthorized_client"}, {"user_code": "CODIGO-PRUEBA"}):
            with self.subTest(flujo=flujo):
                self.aplicacion.initiate_device_flow.return_value = flujo
                with self.assertRaises(oauth.AutorizacionMicrosoftError):
                    oauth.autorizar_cuenta_microsoft(CLIENT_ID, CORREO, mostrar=lambda _: None)
        self.aplicacion.acquire_token_by_device_flow.assert_not_called()
        self.persistencia.save.assert_not_called()


class TestClientePublicoMicrosoft(unittest.TestCase):
    def test_utiliza_cuentas_personales_sin_secreto_de_cliente(self):
        cache = MagicMock()
        with patch.object(oauth.msal, "PublicClientApplication") as construir:
            oauth.crear_aplicacion_microsoft(CLIENT_ID, cache)
        construir.assert_called_once_with(
            client_id=CLIENT_ID,
            authority="https://login.microsoftonline.com/consumers",
            token_cache=cache,
            timeout=10
        )


class TestComprobacionMicrosoft(unittest.TestCase):
    def test_comprobar_no_inicia_autorizacion_interactiva(self):
        from scripts import autorizar_correo_microsoft as script

        with patch.object(script, "obtener_configuracion_correo") as configurar, \
                patch.object(script, "crear_persistencia_microsoft") as persistir, \
                patch.object(script, "autorizar_cuenta_microsoft") as autorizar, \
                patch("builtins.print"):
            configurar.return_value.client_id = CLIENT_ID
            configurar.return_value.usuario = CORREO
            configurar.return_value.transporte = "graph"
            self.assertEqual(script.main(["--comprobar"]), 0)
            persistir.assert_called_once_with(CLIENT_ID, CORREO, "graph")
            autorizar.assert_not_called()

    def test_script_autoriza_el_transporte_configurado(self):
        from scripts import autorizar_correo_microsoft as script

        with patch.object(script, "obtener_configuracion_correo") as configurar, \
                patch.object(script, "autorizar_cuenta_microsoft") as autorizar:
            configurar.return_value.client_id = CLIENT_ID
            configurar.return_value.usuario = CORREO
            configurar.return_value.transporte = "graph"
            self.assertEqual(script.main([]), 0)
            self.assertEqual(autorizar.call_args.args, (CLIENT_ID, CORREO))
            self.assertEqual(autorizar.call_args.kwargs["transporte"], "graph")

    def test_comprobar_devuelve_error_si_almacen_seguro_falla(self):
        from scripts import autorizar_correo_microsoft as script

        with patch.object(script, "obtener_configuracion_correo"), \
                patch.object(script, "crear_persistencia_microsoft", side_effect=RuntimeError("secreto")), \
                patch.object(script, "autorizar_cuenta_microsoft") as autorizar, \
                patch("builtins.print") as imprimir:
            self.assertEqual(script.main(["--comprobar"]), 1)
            self.assertNotIn("secreto", str(imprimir.call_args))
            autorizar.assert_not_called()


if __name__ == "__main__":
    unittest.main()
