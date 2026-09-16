import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from app.services.progreso_service import (
    LetraNoEncontradaError,
    UsuarioNoEncontradoError,
    registrar_progreso,
)


class TestServicioProgreso(unittest.TestCase):

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
    def test_registra_letra_aprendida(
        self,
        conexion_simulada,
    ):
        cursor = self.preparar_conexion(conexion_simulada)

        progreso_esperado = {
            "id_progreso": 10,
            "id_usuario": 9,
            "id_letra": 1,
            "cantidad_intentos": 0,
            "cantidad_aciertos": 0,
            "dominada": True,
            "fecha_ultima_practica": None,
            "fecha_actualizacion": datetime(
                2026, 9, 16, tzinfo=timezone.utc
            ),
        }

        cursor.fetchone.side_effect = [
            {"id_usuario": 9},
            {"id_letra": 1},
            progreso_esperado,
        ]

        resultado = registrar_progreso(
            id_usuario=9,
            id_letra=1,
        )

        self.assertEqual(resultado, progreso_esperado)

        parametros = [
            llamada.args[1]
            for llamada in cursor.execute.call_args_list
        ]

        self.assertEqual(
            parametros,
            [(9,), (1,), (9, 1)],
        )

    @patch("app.services.progreso_service.obtener_conexion")
    def test_rechaza_usuario_inexistente(
        self,
        conexion_simulada,
    ):
        cursor = self.preparar_conexion(conexion_simulada)
        cursor.fetchone.return_value = None

        with self.assertRaisesRegex(
            UsuarioNoEncontradoError,
            "El usuario no existe",
        ):
            registrar_progreso(
                id_usuario=999999,
                id_letra=1,
            )

        cursor.execute.assert_called_once()
        self.assertEqual(
            cursor.execute.call_args.args[1],
            (999999,),
        )

    @patch("app.services.progreso_service.obtener_conexion")
    def test_rechaza_letra_inexistente(
        self,
        conexion_simulada,
    ):
        cursor = self.preparar_conexion(conexion_simulada)

        cursor.fetchone.side_effect = [
            {"id_usuario": 9},
            None,
        ]

        with self.assertRaisesRegex(
            LetraNoEncontradaError,
            "La letra no existe",
        ):
            registrar_progreso(
                id_usuario=9,
                id_letra=999999,
            )

        self.assertEqual(cursor.execute.call_count, 2)
        self.assertEqual(
            cursor.execute.call_args.args[1],
            (999999,),
        )


if __name__ == "__main__":
    unittest.main()