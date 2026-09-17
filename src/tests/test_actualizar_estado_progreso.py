import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from app.services.progreso_service import (
    ProgresoNoEncontradoError,
    actualizar_estado_progreso,
)


class TestActualizarEstadoProgreso(unittest.TestCase):

    def preparar_conexion(self, conexion_simulada):
        conexion = MagicMock()
        cursor = MagicMock()

        conexion_simulada.return_value.__enter__.return_value = (
            conexion
        )
        conexion.cursor.return_value.__enter__.return_value = (
            cursor
        )

        return cursor

    @patch("app.services.progreso_service.obtener_conexion")
    def test_actualiza_ambos_estados(self, conexion_simulada):
        cursor = self.preparar_conexion(conexion_simulada)

        for estado in (True, False):
            with self.subTest(dominada=estado):
                cursor.reset_mock()

                progreso_esperado = {
                    "id_progreso": 10,
                    "id_usuario": 9,
                    "id_letra": 1,
                    "cantidad_intentos": 7,
                    "cantidad_aciertos": 5,
                    "dominada": estado,
                    "fecha_ultima_practica": None,
                    "fecha_actualizacion": datetime(
                        2026, 9, 17, tzinfo=timezone.utc
                    ),
                }

                cursor.fetchone.return_value = progreso_esperado

                resultado = actualizar_estado_progreso(
                    id_usuario=9,
                    id_letra=1,
                    dominada=estado,
                )

                self.assertEqual(resultado, progreso_esperado)

                cursor.execute.assert_called_once()
                self.assertEqual(
                    cursor.execute.call_args.args[1],
                    (estado, 9, 1),
                )

    @patch("app.services.progreso_service.obtener_conexion")
    def test_rechaza_progreso_inexistente(
        self,
        conexion_simulada,
    ):
        cursor = self.preparar_conexion(conexion_simulada)
        cursor.fetchone.return_value = None

        with self.assertRaisesRegex(
            ProgresoNoEncontradoError,
            "No existe progreso para este usuario y esta letra",
        ):
            actualizar_estado_progreso(
                id_usuario=9,
                id_letra=1,
                dominada=True,
            )

        cursor.execute.assert_called_once()

    @patch("app.services.progreso_service.obtener_conexion")
    def test_rechaza_estados_invalidos(
        self,
        conexion_simulada,
    ):
        valores_invalidos = [
            "true",
            "false",
            "aprendida",
            1,
            0,
            None,
        ]

        for valor in valores_invalidos:
            with self.subTest(estado=valor):
                with self.assertRaisesRegex(
                    ValueError,
                    "El estado dominada debe ser True o False",
                ):
                    actualizar_estado_progreso(
                        id_usuario=9,
                        id_letra=1,
                        dominada=valor,
                    )

        conexion_simulada.assert_not_called()


if __name__ == "__main__":
    unittest.main()