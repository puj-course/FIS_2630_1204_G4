import os
import unittest
from unittest.mock import patch

from app.services.aprendizaje_service import evaluar_aprendizaje
from conf.config import (
    ConfiguracionAprendizajeError,
    obtener_minimo_aciertos,
)


class TestConfiguracionAprendizaje(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.dict(os.environ))
        os.environ.pop("APRENDIZAJE_MIN_ACIERTOS", None)

    def test_utiliza_tres_si_no_hay_configuracion(self):
        self.assertEqual(obtener_minimo_aciertos(), 3)

    def test_acepta_enteros_positivos(self):
        for valor in ("1", "3", "5", "10"):
            with self.subTest(valor=valor):
                os.environ["APRENDIZAJE_MIN_ACIERTOS"] = valor

                self.assertEqual(
                    obtener_minimo_aciertos(),
                    int(valor),
                )

    def test_rechaza_configuracion_invalida(self):
        for valor in ("", "0", "-1", "2.5", "abc"):
            with self.subTest(valor=valor):
                os.environ["APRENDIZAJE_MIN_ACIERTOS"] = valor

                with self.assertRaises(ConfiguracionAprendizajeError):
                    obtener_minimo_aciertos()


class TestServicioAprendizaje(unittest.TestCase):
    def setUp(self):
        self.enterContext(
            patch.dict(
                os.environ,
                {"APRENDIZAJE_MIN_ACIERTOS": "3"},
            )
        )

        self.obtener_conexion = self.enterContext(
            patch("app.services.aprendizaje_service.obtener_conexion")
        )
        self.contar_aciertos = self.enterContext(
            patch("app.services.aprendizaje_service.contar_aciertos_letra")
        )
        self.registrar_aprendizaje = self.enterContext(
            patch("app.services.aprendizaje_service.registrar_aprendizaje")
        )

        self.conexion = self.obtener_conexion.return_value
        self.conexion.__enter__.return_value = self.conexion
        self.conexion.__exit__.return_value = False

        contexto_cursor = self.conexion.cursor.return_value
        contexto_cursor.__exit__.return_value = False
        self.cursor = contexto_cursor.__enter__.return_value

        self.progreso = {
            "id_progreso": 20,
            "id_usuario": 7,
            "id_letra": 2,
            "dominada": True,
        }

        self.contar_aciertos.return_value = 3
        self.registrar_aprendizaje.return_value = self.progreso

    def evaluar(self):
        return evaluar_aprendizaje(
            id_usuario=7,
            id_letra=2,
        )

    def test_no_registra_antes_de_alcanzar_el_minimo(self):
        for aciertos in (0, 1, 2):
            with self.subTest(aciertos=aciertos):
                self.contar_aciertos.reset_mock()
                self.registrar_aprendizaje.reset_mock()
                self.contar_aciertos.return_value = aciertos

                resultado = self.evaluar()

                self.assertIsNone(resultado)
                self.contar_aciertos.assert_called_once_with(
                    cursor=self.cursor,
                    id_usuario=7,
                    id_letra=2,
                )
                self.registrar_aprendizaje.assert_not_called()

    def test_registra_al_alcanzar_o_superar_el_minimo(self):
        for aciertos in (3, 4, 10):
            with self.subTest(aciertos=aciertos):
                self.contar_aciertos.reset_mock()
                self.registrar_aprendizaje.reset_mock()
                self.contar_aciertos.return_value = aciertos

                resultado = self.evaluar()

                self.assertEqual(resultado, self.progreso)
                self.contar_aciertos.assert_called_once_with(
                    cursor=self.cursor,
                    id_usuario=7,
                    id_letra=2,
                )
                self.registrar_aprendizaje.assert_called_once_with(
                    cursor=self.cursor,
                    id_usuario=7,
                    id_letra=2,
                )

    def test_respeta_un_minimo_configurado_diferente(self):
        os.environ["APRENDIZAJE_MIN_ACIERTOS"] = "5"
        self.contar_aciertos.return_value = 3

        self.assertIsNone(self.evaluar())
        self.registrar_aprendizaje.assert_not_called()

        self.contar_aciertos.return_value = 5

        self.assertEqual(self.evaluar(), self.progreso)
        self.registrar_aprendizaje.assert_called_once_with(
            cursor=self.cursor,
            id_usuario=7,
            id_letra=2,
        )

    def test_devuelve_none_si_el_repositorio_no_modifico_progreso(self):
        # Simula que el repositorio encontró la letra ya aprendida.
        self.registrar_aprendizaje.return_value = None

        self.assertIsNone(self.evaluar())
        self.registrar_aprendizaje.assert_called_once_with(
            cursor=self.cursor,
            id_usuario=7,
            id_letra=2,
        )

    def test_configuracion_invalida_impide_acceder_a_la_base(self):
        os.environ["APRENDIZAJE_MIN_ACIERTOS"] = "0"

        with self.assertRaises(ConfiguracionAprendizajeError):
            self.evaluar()

        self.obtener_conexion.assert_not_called()
        self.contar_aciertos.assert_not_called()
        self.registrar_aprendizaje.assert_not_called()

    def test_propaga_error_de_conexion(self):
        self.obtener_conexion.side_effect = RuntimeError(
            "Fallo de conexión"
        )

        with self.assertRaisesRegex(RuntimeError, "Fallo de conexión"):
            self.evaluar()

        self.contar_aciertos.assert_not_called()
        self.registrar_aprendizaje.assert_not_called()

    def test_error_de_conteo_impide_registrar_aprendizaje(self):
        self.contar_aciertos.side_effect = RuntimeError(
            "Fallo de conteo"
        )

        with self.assertRaisesRegex(RuntimeError, "Fallo de conteo"):
            self.evaluar()

        self.registrar_aprendizaje.assert_not_called()
        self.assertIs(
            self.conexion.__exit__.call_args.args[0],
            RuntimeError,
        )

    def test_propaga_error_al_guardar_aprendizaje(self):
        self.registrar_aprendizaje.side_effect = RuntimeError(
            "Fallo al guardar"
        )

        with self.assertRaisesRegex(RuntimeError, "Fallo al guardar"):
            self.evaluar()

        self.assertIs(
            self.conexion.__exit__.call_args.args[0],
            RuntimeError,
        )

    def test_no_devuelve_exito_si_falla_el_commit(self):
        self.conexion.__exit__.side_effect = RuntimeError(
            "Fallo de commit"
        )

        with self.assertRaisesRegex(RuntimeError, "Fallo de commit"):
            self.evaluar()

        self.registrar_aprendizaje.assert_called_once()


if __name__ == "__main__":
    unittest.main()