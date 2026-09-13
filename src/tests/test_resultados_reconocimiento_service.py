import unittest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

from app.services.resultados_reconocimiento_service import (
    LetraDetectadaNoEncontradaError,
    LetraObjetivoNoEncontradaError,
    registrar_resultado_reconocimiento,
)


class TestServicioResultadosReconocimiento(unittest.TestCase):

    def preparar_conexion(self, obtener_conexion_simulada):
        conexion = MagicMock()
        cursor = MagicMock()

        obtener_conexion_simulada.return_value.__enter__.return_value = (
            conexion
        )

        conexion.cursor.return_value.__enter__.return_value = cursor

        return cursor

    @patch(
        "app.services.resultados_reconocimiento_service.obtener_conexion"
    )
    def test_crea_sesion_y_registra_resultado_correcto(
        self,
        obtener_conexion_simulada,
    ):
        cursor = self.preparar_conexion(
            obtener_conexion_simulada
        )

        fecha = datetime(
            2026,
            9,
            13,
            tzinfo=timezone.utc,
        )

        cursor.fetchone.side_effect = [
            {
                "id_letra": 1,
                "letra": "A",
            },
            {
                "id_letra": 1,
                "letra": "A",
            },
            {
                "id_sesion": 31,
            },
            {
                "id_resultado": 48,
                "confianza": Decimal("0.9500"),
                "es_correcto": True,
                "fecha_resultado": fecha,
            },
        ]

        resultado = registrar_resultado_reconocimiento(
            id_usuario=9,
            id_letra_objetivo=1,
            letra_detectada="A",
            confianza=0.95,
        )

        self.assertEqual(resultado["id_usuario"], 9)
        self.assertEqual(resultado["id_sesion"], 31)
        self.assertEqual(resultado["id_resultado"], 48)
        self.assertEqual(resultado["letra_objetivo"], "A")
        self.assertEqual(resultado["letra_detectada"], "A")
        self.assertEqual(resultado["confianza"], 0.95)
        self.assertTrue(resultado["es_correcto"])

        self.assertEqual(cursor.execute.call_count, 4)

        parametros_sesion = (
            cursor.execute.call_args_list[2].args[1]
        )

        self.assertEqual(parametros_sesion, (9,))

        parametros_resultado = (
            cursor.execute.call_args_list[3].args[1]
        )

        self.assertEqual(
            parametros_resultado,
            (31, 1, 1, 0.95, True),
        )

    @patch(
        "app.services.resultados_reconocimiento_service.obtener_conexion"
    )
    def test_registra_resultado_incorrecto(
        self,
        obtener_conexion_simulada,
    ):
        cursor = self.preparar_conexion(
            obtener_conexion_simulada
        )

        cursor.fetchone.side_effect = [
            {
                "id_letra": 1,
                "letra": "A",
            },
            {
                "id_letra": 2,
                "letra": "B",
            },
            {
                "id_sesion": 32,
            },
            {
                "id_resultado": 49,
                "confianza": Decimal("0.8300"),
                "es_correcto": False,
                "fecha_resultado": datetime.now(timezone.utc),
            },
        ]

        resultado = registrar_resultado_reconocimiento(
            id_usuario=9,
            id_letra_objetivo=1,
            letra_detectada="B",
            confianza=0.83,
        )

        self.assertFalse(resultado["es_correcto"])

        parametros_resultado = (
            cursor.execute.call_args_list[3].args[1]
        )

        self.assertEqual(
            parametros_resultado,
            (32, 1, 2, 0.83, False),
        )

    @patch(
        "app.services.resultados_reconocimiento_service.obtener_conexion"
    )
    def test_rechaza_letra_objetivo_inexistente(
        self,
        obtener_conexion_simulada,
    ):
        cursor = self.preparar_conexion(
            obtener_conexion_simulada
        )

        cursor.fetchone.return_value = None

        with self.assertRaises(
            LetraObjetivoNoEncontradaError
        ):
            registrar_resultado_reconocimiento(
                id_usuario=9,
                id_letra_objetivo=999999,
                letra_detectada="A",
                confianza=0.95,
            )

        self.assertEqual(cursor.execute.call_count, 1)

    @patch(
        "app.services.resultados_reconocimiento_service.obtener_conexion"
    )
    def test_rechaza_letra_detectada_inexistente(
        self,
        obtener_conexion_simulada,
    ):
        cursor = self.preparar_conexion(
            obtener_conexion_simulada
        )

        cursor.fetchone.side_effect = [
            {
                "id_letra": 1,
                "letra": "A",
            },
            None,
        ]

        with self.assertRaises(
            LetraDetectadaNoEncontradaError
        ):
            registrar_resultado_reconocimiento(
                id_usuario=9,
                id_letra_objetivo=1,
                letra_detectada="?",
                confianza=0.95,
            )

        self.assertEqual(cursor.execute.call_count, 2)


if __name__ == "__main__":
    unittest.main()