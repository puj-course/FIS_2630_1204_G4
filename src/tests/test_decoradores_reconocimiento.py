import unittest
from unittest.mock import patch

from app.vision.decoradores_reconocimiento import (
    DecoradorMedicionTiempo,
    DecoradorReconocimiento,
)
from app.vision.estrategia_reconocimiento import (
    EstrategiaReconocimiento,
)
from app.vision.reconocimiento import reconocer_mano


class EstrategiaPrueba(EstrategiaReconocimiento):
    """Estrategia simulada para comprobar el decorador."""

    def __init__(self, resultado=None, error=None):
        self.resultado = resultado
        self.error = error
        self.llamadas = []

    def reconocer(self, mano, fotogramas=()):
        self.llamadas.append((mano, fotogramas))

        if self.error is not None:
            raise self.error

        return self.resultado


class TestDecoradorReconocimiento(unittest.TestCase):

    def test_decorador_base_delega_reconocimiento(self):
        mano = object()
        fotogramas = ("fotograma1", "fotograma2")
        resultado = {
            "letra": "A",
            "requiere_movimiento": False,
        }

        estrategia = EstrategiaPrueba(resultado)
        decorador = DecoradorReconocimiento(estrategia)

        respuesta = decorador.reconocer(mano, fotogramas)

        self.assertIs(respuesta, resultado)
        self.assertEqual(
            estrategia.llamadas,
            [(mano, fotogramas)],
        )

    def test_mide_tiempo_de_reconocimiento(self):
        estrategia = EstrategiaPrueba({
            "letra": "A",
            "requiere_movimiento": False,
        })

        decorador = DecoradorMedicionTiempo(estrategia)

        with patch(
            "app.vision.decoradores_reconocimiento.time.perf_counter",
            side_effect=[10.0, 10.025],
        ), patch(
            "app.vision.decoradores_reconocimiento._logger.info"
        ) as registrar:

            resultado = decorador.reconocer(object())

        self.assertEqual(resultado["letra"], "A")
        registrar.assert_called_once()

        argumentos = registrar.call_args.args

        self.assertEqual(argumentos[1], "EstrategiaPrueba")
        self.assertAlmostEqual(argumentos[2], 25.0, places=3)
        self.assertEqual(argumentos[3], "reconocida")

    def test_registra_reconocimiento_sin_coincidencia(self):
        estrategia = EstrategiaPrueba({
            "letra": None,
            "requiere_movimiento": False,
        })

        decorador = DecoradorMedicionTiempo(estrategia)

        with patch(
            "app.vision.decoradores_reconocimiento._logger.info"
        ) as registrar:

            resultado = decorador.reconocer(object())

        self.assertIsNone(resultado["letra"])
        registrar.assert_called_once()

        argumentos = registrar.call_args.args

        self.assertEqual(
            argumentos[3],
            "sin_coincidencia",
        )

    def test_registra_tiempo_incluso_con_error(self):
        estrategia = EstrategiaPrueba(
            error=ValueError("Error de prueba")
        )

        decorador = DecoradorMedicionTiempo(estrategia)

        with patch(
            "app.vision.decoradores_reconocimiento._logger.info"
        ) as registrar:

            with self.assertRaisesRegex(
                ValueError,
                "Error de prueba",
            ):
                decorador.reconocer(object())

        registrar.assert_called_once()

        argumentos = registrar.call_args.args
        self.assertGreaterEqual(argumentos[2], 0)
        self.assertEqual(argumentos[3], "error")

    @patch(
        "app.vision.reconocimiento.reconocer_consonante_estatica",
        return_value="B",
    )
    @patch(
        "app.vision.reconocimiento.reconocer_vocal"
    )
    def test_integracion_reconocimiento_estatico(
        self,
        reconocer_vocal,
        reconocer_consonante,
    ):
        with patch(
            "app.vision.decoradores_reconocimiento._logger.info"
        ) as registrar:

            resultado = reconocer_mano(
                mano=object(),
                modo="estatica",
            )

        self.assertEqual(resultado["letra"], "B")
        self.assertFalse(resultado["requiere_movimiento"])

        reconocer_consonante.assert_called_once()
        reconocer_vocal.assert_not_called()

        registrar.assert_called_once()
        self.assertEqual(
            registrar.call_args.args[1],
            "ReconocimientoEstatico",
        )

    @patch(
        "app.vision.reconocimiento.reconocer_letra_movimiento",
        return_value="J",
    )
    @patch(
        "app.vision.reconocimiento.reconocer_consonante_estatica"
    )
    def test_integracion_reconocimiento_movimiento(
        self,
        reconocer_consonante,
        reconocer_movimiento,
    ):
        mano = object()
        fotogramas = ("fotograma1", "fotograma2")

        with patch(
            "app.vision.decoradores_reconocimiento._logger.info"
        ) as registrar:

            resultado = reconocer_mano(
                mano=mano,
                fotogramas=fotogramas,
                modo="movimiento",
            )

        self.assertEqual(resultado["letra"], "J")
        self.assertTrue(resultado["requiere_movimiento"])

        reconocer_movimiento.assert_called_once_with(
            mano,
            fotogramas,
        )

        reconocer_consonante.assert_not_called()

        registrar.assert_called_once()
        self.assertEqual(
            registrar.call_args.args[1],
            "ReconocimientoMovimiento",
        )


if __name__ == "__main__":
    unittest.main()
