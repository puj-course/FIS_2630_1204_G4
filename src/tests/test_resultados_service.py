import unittest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

from app.services.resultados_service import (
    LetraNoEncontradaError,
    registrar_resultado,
)
from src.schemas.resultados import ResultadoRegistrado


class TestRegistroResultadosPorSesion(unittest.TestCase):
    @patch("app.services.resultados_service.obtener_conexion")
    def test_registra_aciertos_y_errores(self, obtener_conexion):
        for detectada, ids_existentes, correcto in (
            (1, [1], True),
            (2, [1, 2], False),
        ):
            with self.subTest(detectada=detectada):
                conexion = MagicMock()
                cursor = MagicMock()

                obtener_conexion.return_value.__enter__.return_value = (
                    conexion
                )
                conexion.cursor.return_value.__enter__.return_value = (
                    cursor
                )

                almacenado = {
                    "id_resultado": 20,
                    "id_sesion": 10,
                    "id_letra_objetivo": 1,
                    "id_letra_detectada": detectada,
                    "confianza": Decimal("0.9500"),
                    "es_correcto": correcto,
                    "fecha_resultado": datetime.now(timezone.utc),
                }

                cursor.fetchone.side_effect = [
                    {"id_usuario": 9},
                    almacenado,
                ]
                cursor.fetchall.return_value = [
                    {"id_letra": identificador}
                    for identificador in ids_existentes
                ]

                resultado = registrar_resultado(
                    id_usuario=9,
                    id_sesion=10,
                    id_letra_objetivo=1,
                    id_letra_detectada=detectada,
                    confianza=0.95,
                )

                self.assertEqual(resultado, almacenado)
                self.assertEqual(cursor.execute.call_count, 3)
                self.assertEqual(
                    cursor.execute.call_args.args[1],
                    (10, 1, detectada, 0.95, correcto),
                )

                salida = ResultadoRegistrado(**resultado)
                self.assertIs(salida.es_correcto, correcto)
                self.assertEqual(salida.id_sesion, 10)

    @patch("app.services.resultados_service.obtener_conexion")
    def test_rechaza_letras_inexistentes(self, obtener_conexion):
        for ids_existentes in ([], [1], [2]):
            with self.subTest(ids_existentes=ids_existentes):
                conexion = MagicMock()
                cursor = MagicMock()

                obtener_conexion.return_value.__enter__.return_value = (
                    conexion
                )
                conexion.cursor.return_value.__enter__.return_value = (
                    cursor
                )

                cursor.fetchone.return_value = {"id_usuario": 9}
                cursor.fetchall.return_value = [
                    {"id_letra": identificador}
                    for identificador in ids_existentes
                ]

                with self.assertRaises(LetraNoEncontradaError):
                    registrar_resultado(
                        id_usuario=9,
                        id_sesion=10,
                        id_letra_objetivo=1,
                        id_letra_detectada=2,
                        confianza=0.95,
                    )

                # Solo consulta sesión y letras; no ejecuta la inserción.
                self.assertEqual(cursor.execute.call_count, 2)


if __name__ == "__main__":
    unittest.main()