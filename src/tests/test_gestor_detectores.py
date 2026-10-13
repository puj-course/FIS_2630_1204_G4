import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, call, patch

from app.vision.gestor_detectores import (
    GestorDetectores,
    GestorDetectoresCompartido,
)


class TestGestorDetectores(unittest.TestCase):
    def setUp(self):
        self.gestor = GestorDetectoresCompartido()
        self.gestor.cerrar()

        parche = patch(
            "app.vision.gestor_detectores.DetectorMano"
        )
        self.constructor = parche.start()
        self.addCleanup(parche.stop)
        self.addCleanup(self.gestor.cerrar)

        self.imagen = object()

    def test_comparte_instancia_entre_llamadas_y_hilos(self):
        with ThreadPoolExecutor(max_workers=8) as ejecutor:
            instancias = list(
                ejecutor.map(
                    lambda _: GestorDetectoresCompartido(),
                    range(32),
                )
            )

        self.assertIsInstance(self.gestor, GestorDetectores)

        for instancia in instancias:
            self.assertIs(instancia, self.gestor)

        self.constructor.assert_not_called()

    def test_reutiliza_detector_al_solicitar_el_gestor_otra_vez(self):
        detector = self.constructor.return_value

        primera_respuesta = self.gestor.detectar(self.imagen)

        otro_gestor = GestorDetectoresCompartido()
        segunda_respuesta = otro_gestor.detectar(self.imagen)

        self.constructor.assert_called_once_with(
            modo_video=False,
        )
        self.assertEqual(
            detector.detectar.call_args_list,
            [
                call(self.imagen, None),
                call(self.imagen, None),
            ],
        )
        self.assertIs(
            primera_respuesta,
            detector.detectar.return_value,
        )
        self.assertIs(
            segunda_respuesta,
            detector.detectar.return_value,
        )

    def test_mantiene_detectores_separados_para_imagen_y_video(self):
        detector_imagen = Mock()
        detector_video = Mock()

        self.constructor.side_effect = [
            detector_imagen,
            detector_video,
        ]

        self.gestor.detectar(self.imagen)
        self.gestor.detectar(self.imagen, tiempo_actual=0)
        self.gestor.detectar(self.imagen)
        self.gestor.detectar(self.imagen, tiempo_actual=10)

        self.assertEqual(
            self.constructor.call_args_list,
            [
                call(modo_video=False),
                call(modo_video=True),
            ],
        )
        self.assertEqual(
            detector_imagen.detectar.call_args_list,
            [
                call(self.imagen, None),
                call(self.imagen, None),
            ],
        )
        self.assertEqual(
            detector_video.detectar.call_args_list,
            [
                call(self.imagen, 0),
                call(self.imagen, 10),
            ],
        )

    def test_cierra_ambos_detectores_y_permite_volver_a_crearlos(self):
        detector_imagen = Mock()
        detector_video = Mock()
        detector_nuevo = Mock()

        self.constructor.side_effect = [
            detector_imagen,
            detector_video,
            detector_nuevo,
        ]

        self.gestor.detectar(self.imagen)
        self.gestor.detectar(self.imagen, tiempo_actual=10)

        self.gestor.cerrar()
        self.gestor.cerrar()

        detector_imagen.cerrar.assert_called_once_with()
        detector_video.cerrar.assert_called_once_with()

        respuesta = self.gestor.detectar(self.imagen)

        self.assertEqual(self.constructor.call_count, 3)
        detector_nuevo.detectar.assert_called_once_with(
            self.imagen,
            None,
        )
        self.assertIs(
            respuesta,
            detector_nuevo.detectar.return_value,
        )


if __name__ == "__main__":
    unittest.main()