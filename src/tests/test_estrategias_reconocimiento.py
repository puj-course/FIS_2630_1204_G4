import unittest
from unittest.mock import patch

from app.vision.reconocimiento import (
    ReconocedorMano,
    ReconocimientoEstatico,
    ReconocimientoMovimiento,
    reconocer_mano,
)


class TestEstrategiasReconocimiento(unittest.TestCase):
    def setUp(self):
        self.mano = object()
        self.fotogramas = ()

        self.consonante = self.iniciar_parche(
            "app.vision.reconocimiento.reconocer_consonante_estatica"
        )
        self.vocal = self.iniciar_parche(
            "app.vision.reconocimiento.reconocer_vocal"
        )
        self.movimiento = self.iniciar_parche(
            "app.vision.reconocimiento.reconocer_letra_movimiento"
        )

    def iniciar_parche(self, destino):
        parche = patch(destino)
        simulacion = parche.start()
        self.addCleanup(parche.stop)
        return simulacion

    def test_estatica_conserva_prioridad_y_resultados(self):
        casos = [
            ("B", "A", "B", False),
            (None, "A", "A", True),
            (None, None, None, True),
        ]

        for consonante, vocal, esperada, consulta_vocal in casos:
            with self.subTest(consonante=consonante, vocal=vocal):
                self.consonante.reset_mock()
                self.vocal.reset_mock()
                self.movimiento.reset_mock()

                self.consonante.return_value = consonante
                self.vocal.return_value = vocal

                resultado = reconocer_mano(self.mano)

                self.assertEqual(
                    resultado,
                    {
                        "letra": esperada,
                        "requiere_movimiento": False,
                    },
                )
                self.consonante.assert_called_once_with(self.mano)
                self.movimiento.assert_not_called()

                if consulta_vocal:
                    self.vocal.assert_called_once_with(self.mano)
                else:
                    self.vocal.assert_not_called()

    def test_movimiento_recibe_fotogramas_y_no_consulta_estaticas(self):
        # Los algoritmos se simulan para comprobar la delegación.
        fotogramas = (object(), object())
        self.movimiento.return_value = "J"

        resultado = reconocer_mano(
            self.mano,
            fotogramas=fotogramas,
            modo="movimiento",
        )

        self.assertEqual(
            resultado,
            {"letra": "J", "requiere_movimiento": True},
        )
        self.movimiento.assert_called_once_with(
            self.mano,
            fotogramas,
        )
        self.consonante.assert_not_called()
        self.vocal.assert_not_called()

    def test_contexto_permite_intercambiar_estrategias(self):
        self.consonante.return_value = "B"
        self.movimiento.return_value = "J"

        contexto = ReconocedorMano(ReconocimientoEstatico())

        estatico = contexto.reconocer(self.mano)

        contexto.cambiar_estrategia(ReconocimientoMovimiento())

        movimiento = contexto.reconocer(
            self.mano,
            self.fotogramas,
        )

        self.assertEqual(
            estatico,
            {"letra": "B", "requiere_movimiento": False},
        )
        self.assertEqual(
            movimiento,
            {"letra": "J", "requiere_movimiento": True},
        )
        self.consonante.assert_called_once_with(self.mano)
        self.movimiento.assert_called_once_with(
            self.mano,
            self.fotogramas,
        )
        self.vocal.assert_not_called()

    def test_modo_invalido_no_ejecuta_algoritmos(self):
        with self.assertRaisesRegex(
            ValueError,
            "El modo debe ser 'estatica' o 'movimiento'",
        ):
            reconocer_mano(self.mano, modo="invalido")

        self.consonante.assert_not_called()
        self.vocal.assert_not_called()
        self.movimiento.assert_not_called()


if __name__ == "__main__":
    unittest.main()