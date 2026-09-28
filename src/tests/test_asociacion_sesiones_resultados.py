import unittest
from unittest.mock import MagicMock, patch

from app.services.resultados_service import (
    SesionNoEncontradaError,
    UsuarioSesionError,
    registrar_resultado,
)


class TestAsociacionSesionesResultados(unittest.TestCase):

    def setUp(self):
        parche = patch(
            "app.services.resultados_service.obtener_conexion"
        )

        self.obtener_conexion = parche.start()
        self.addCleanup(parche.stop)

        self.conexion = MagicMock()
        self.cursor = MagicMock()

        self.obtener_conexion.return_value.__enter__.return_value = (
            self.conexion
        )

        self.conexion.cursor.return_value.__enter__.return_value = (
            self.cursor
        )


    def test_no_permite_resultado_sin_sesion_existente(self):

        self.cursor.fetchone.return_value = None

        with self.assertRaises(
            SesionNoEncontradaError
        ):
            registrar_resultado(
                id_usuario=10,
                id_sesion=999,
                id_letra_objetivo=1,
                id_letra_detectada=1,
                confianza=0.95,
            )
        self.assertEqual(self.cursor.execute.call_count, 1)
        self.cursor.fetchall.assert_not_called()

    def test_no_permite_resultado_en_sesion_de_otro_usuario(self):

        self.cursor.fetchone.return_value = {
            "id_usuario": 20,
        }

        with self.assertRaises(
            UsuarioSesionError
        ):
            registrar_resultado(
                id_usuario=10,
                id_sesion=5,
                id_letra_objetivo=1,
                id_letra_detectada=1,
                confianza=0.95,
            )
        self.assertEqual(self.cursor.execute.call_count, 1)
        self.cursor.fetchall.assert_not_called()

if __name__ == "__main__":
    unittest.main()