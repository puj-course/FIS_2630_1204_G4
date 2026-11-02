
import unittest
from unittest.mock import patch

from app.vision.decoradores_reconocimiento import (
    DecoradorMedicionTiempo,
)
from app.vision.reconocimiento import (
    ReconocimientoEstatico,
    reconocer_mano,
)


class TestCasosBordeReconocimiento(unittest.TestCase):

    @patch(
        "app.vision.reconocimiento.reconocer_letra_movimiento",
        return_value=None,
    )
    def test_movimiento_sin_fotogramas(self, reconocer_movimiento):
        # Arrange
        mano = object()
        fotogramas = ()

        # Act
        resultado = reconocer_mano(
            mano=mano,
            fotogramas=fotogramas,
            modo="movimiento",
        )

        # Assert
        self.assertIsNone(resultado["letra"])
        self.assertTrue(resultado["requiere_movimiento"])

        reconocer_movimiento.assert_called_once_with(
            mano,
            fotogramas,
        )

    @patch(
        "app.vision.reconocimiento.reconocer_consonante_estatica",
        return_value="A",
    )
    def test_medicion_con_duracion_cero(self, reconocer_estatico):
        # Arrange
        decorador = DecoradorMedicionTiempo(
            ReconocimientoEstatico()
        )

        with patch(
            "app.vision.decoradores_reconocimiento.time.perf_counter",
            side_effect=[10.0, 10.0],
        ), patch(
            "app.vision.decoradores_reconocimiento._logger.info"
        ) as registrar:

            # Act
            resultado = decorador.reconocer(object())

        # Assert
        self.assertEqual(resultado["letra"], "A")
        reconocer_estatico.assert_called_once()
        registrar.assert_called_once()

        argumentos = registrar.call_args.args

        self.assertEqual(
            argumentos[1],
            "ReconocimientoEstatico",
        )
        self.assertEqual(argumentos[2], 0.0)
        self.assertEqual(argumentos[3], "reconocida")


if __name__ == "__main__":
    unittest.main()
