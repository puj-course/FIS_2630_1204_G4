import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from app.services import autenticacion_service
from app.services.cadena_autenticacion import (
    CuentaBloqueadaError,
    ManejadorAutenticacion,
    ManejadorContrasena,
    ManejadorCuentaNoBloqueada,
    ManejadorUsuarioExistente,
    SolicitudAutenticacion,
)

CORREO = "persona.prueba@signia.local"
CONTRASENA = "ClaveSeguraDePrueba123!"


class ManejadorEspia(ManejadorAutenticacion):
    """Eslabón de prueba que registra si la cadena llegó hasta él."""

    def __init__(self, resultado=None):
        super().__init__()
        self.alcanzado = False
        self.resultado = resultado

    def manejar(self, solicitud):
        self.alcanzado = True
        return self.resultado


class TestCadenaAutenticacion(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.password_hash = autenticacion_service.password_hash
        cls.hash_valido = autenticacion_service.generar_hash_contrasena(
            CONTRASENA
        )

    def setUp(self):
        self.usuario = {
            "id_usuario": 7,
            "nombre": "Persona de prueba",
            "correo": CORREO,
            "contrasena_hash": self.hash_valido,
            "rol": "usuario",
            "bloqueado_hasta": None
        }
        self.registrar = MagicMock()
        self.reiniciar = MagicMock()

    def solicitud(self, contrasena=CONTRASENA, usuario=None):
        return SolicitudAutenticacion(
            correo=CORREO,
            contrasena=contrasena,
            usuario=usuario
        )

    def construir_cadena(self, usuario, password_hash=None):
        self.obtener = MagicMock(return_value=usuario)
        cadena = ManejadorUsuarioExistente(self.obtener)
        cadena.establecer_siguiente(
            ManejadorCuentaNoBloqueada()
        ).establecer_siguiente(
            ManejadorContrasena(
                password_hash or self.password_hash,
                self.registrar,
                self.reiniciar
            )
        )
        return cadena

    def test_establecer_siguiente_devuelve_el_manejador_recibido(self):
        primero = ManejadorCuentaNoBloqueada()
        segundo = ManejadorEspia()

        self.assertIs(primero.establecer_siguiente(segundo), segundo)

    def test_cadena_sin_eslabon_final_rechaza_por_defecto(self):
        manejador = ManejadorUsuarioExistente(MagicMock(return_value=self.usuario))

        self.assertIsNone(manejador.manejar(self.solicitud()))

    def test_usuario_inexistente_detiene_la_cadena(self):
        espia = ManejadorEspia(resultado={"id_usuario": 99})
        manejador = ManejadorUsuarioExistente(MagicMock(return_value=None))
        manejador.establecer_siguiente(espia)

        self.assertIsNone(manejador.manejar(self.solicitud()))
        self.assertFalse(espia.alcanzado)

    def test_usuario_existente_pasa_al_siguiente_con_el_usuario(self):
        espia = ManejadorEspia(resultado={"id_usuario": 7})
        obtener = MagicMock(return_value=self.usuario)
        manejador = ManejadorUsuarioExistente(obtener)
        manejador.establecer_siguiente(espia)
        solicitud = self.solicitud()

        self.assertEqual(manejador.manejar(solicitud), {"id_usuario": 7})
        self.assertTrue(espia.alcanzado)
        self.assertIs(solicitud.usuario, self.usuario)
        obtener.assert_called_once_with(CORREO)

    def test_cuenta_bloqueada_lanza_error_y_detiene_la_cadena(self):
        self.usuario["bloqueado_hasta"] = (
            datetime.now(timezone.utc) + timedelta(minutes=5)
        )
        espia = ManejadorEspia()
        manejador = ManejadorCuentaNoBloqueada()
        manejador.establecer_siguiente(espia)

        with self.assertRaises(CuentaBloqueadaError):
            manejador.manejar(self.solicitud(usuario=self.usuario))

        self.assertFalse(espia.alcanzado)

    def test_cuenta_sin_bloqueo_o_con_bloqueo_vencido_pasa_al_siguiente(self):
        for bloqueado_hasta in (
            None, datetime.now(timezone.utc) - timedelta(minutes=5)
        ):
            with self.subTest(bloqueado_hasta=bloqueado_hasta):
                self.usuario["bloqueado_hasta"] = bloqueado_hasta
                espia = ManejadorEspia(resultado={"id_usuario": 7})
                manejador = ManejadorCuentaNoBloqueada()
                manejador.establecer_siguiente(espia)

                resultado = manejador.manejar(
                    self.solicitud(usuario=self.usuario)
                )

                self.assertEqual(resultado, {"id_usuario": 7})
                self.assertTrue(espia.alcanzado)

    def test_contrasena_correcta_reinicia_intentos_y_oculta_el_hash(self):
        manejador = ManejadorContrasena(
            self.password_hash, self.registrar, self.reiniciar
        )

        resultado = manejador.manejar(self.solicitud(usuario=self.usuario))

        self.assertEqual(resultado, {
            "id_usuario": 7,
            "nombre": "Persona de prueba",
            "correo": CORREO,
            "rol": "usuario"
        })
        self.reiniciar.assert_called_once_with(7)
        self.registrar.assert_not_called()

    def test_contrasena_incorrecta_o_hash_no_utilizable_registra_intento(self):
        for contrasena, contrasena_hash in (
            ("clave-incorrecta", self.hash_valido),
            (CONTRASENA, "HASH_DE_PRUEBA_NO_UTILIZABLE")
        ):
            with self.subTest(contrasena_hash=contrasena_hash[:10]):
                self.registrar.reset_mock()
                self.reiniciar.reset_mock()
                self.usuario["contrasena_hash"] = contrasena_hash
                manejador = ManejadorContrasena(
                    self.password_hash, self.registrar, self.reiniciar
                )

                resultado = manejador.manejar(
                    self.solicitud(contrasena=contrasena, usuario=self.usuario)
                )

                self.assertIsNone(resultado)
                self.registrar.assert_called_once_with(7)
                self.reiniciar.assert_not_called()

    def test_cadena_completa_autentica_credenciales_correctas(self):
        cadena = self.construir_cadena(self.usuario)

        resultado = cadena.manejar(self.solicitud())

        self.assertEqual(resultado["id_usuario"], 7)
        self.assertNotIn("contrasena_hash", resultado)
        self.reiniciar.assert_called_once_with(7)

    def test_cadena_completa_no_registra_intento_si_usuario_no_existe(self):
        cadena = self.construir_cadena(None)

        self.assertIsNone(cadena.manejar(self.solicitud()))
        self.registrar.assert_not_called()
        self.reiniciar.assert_not_called()

    def test_cuenta_bloqueada_no_verifica_contrasena_ni_registra_intento(self):
        self.usuario["bloqueado_hasta"] = (
            datetime.now(timezone.utc) + timedelta(minutes=5)
        )
        password_hash = MagicMock()
        cadena = self.construir_cadena(self.usuario, password_hash)

        with self.assertRaises(CuentaBloqueadaError):
            cadena.manejar(self.solicitud())

        password_hash.verify.assert_not_called()
        self.registrar.assert_not_called()
        self.reiniciar.assert_not_called()

    def test_solicitud_no_expone_contrasena_ni_hash_en_repr(self):
        solicitud = self.solicitud(usuario=self.usuario)

        self.assertNotIn(CONTRASENA, repr(solicitud))
        self.assertNotIn(self.hash_valido, repr(solicitud))

    def test_servicio_reexporta_la_misma_excepcion(self):
        self.assertIs(
            autenticacion_service.CuentaBloqueadaError,
            CuentaBloqueadaError
        )


if __name__ == "__main__":
    unittest.main()