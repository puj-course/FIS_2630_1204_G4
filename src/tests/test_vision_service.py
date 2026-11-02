"""Pruebas unitarias para el procesamiento de imágenes de SignIA."""

import base64
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.services import vision_service


class TestVisionService(unittest.TestCase):
    """Valida las funciones de vision_service sin usar una cámara real."""

    def setUp(self):
        # Cada prueba trabaja con un historial independiente.
        parche = patch.dict(vision_service._historiales_movimiento, clear=True)
        parche.start()
        self.addCleanup(parche.stop)

    def test_decodificar_rechaza_base64_invalido_y_vacio(self):
        for contenido in ("@@@", ""):
            with self.subTest(contenido=contenido):
                with self.assertRaises(ValueError):
                    vision_service.decodificar_imagen(contenido)

    def test_decodificar_respeta_limites_de_tamano(self):
        # Límite del texto Base64.
        with self.assertRaisesRegex(ValueError, "tamaño permitido"):
            vision_service.decodificar_imagen("A" * 7_000_001)

        # Se usa un archivo con cabecera PNG, pero mayor a 5 MiB.
        contenido = b"\x89PNG\r\n\x1a\n" + b"x" * (
            vision_service.LIMITE_IMAGEN_BYTES - 7
        )
        codificado = base64.b64encode(contenido).decode("ascii")
        self.assertLessEqual(len(codificado), 7_000_000)

        with self.assertRaisesRegex(ValueError, "5 MiB"):
            vision_service.decodificar_imagen(codificado)

    def test_decodificar_rechaza_formato_no_admitido(self):
        contenido = base64.b64encode(b"GIF89a").decode("ascii")
        with self.assertRaisesRegex(ValueError, "JPEG o PNG"):
            vision_service.decodificar_imagen(contenido)

    def test_decodificar_jpeg_devuelve_imagen(self):
        imagen_esperada = object()
        jpeg_simulado = base64.b64encode(b"\xff\xd8\xffcontenido").decode(
            "ascii"
        )

        with patch(
            "app.services.vision_service.cv2.imdecode",
            return_value=imagen_esperada,
        ) as decodificador:
            resultado = vision_service.decodificar_imagen(jpeg_simulado)

        self.assertIs(resultado, imagen_esperada)
        decodificador.assert_called_once()

    def test_decodificar_rechaza_imagen_que_no_puede_leerse(self):
        jpeg_simulado = base64.b64encode(b"\xff\xd8\xffcorrupto").decode(
            "ascii"
        )

        with patch(
            "app.services.vision_service.cv2.imdecode", return_value=None
        ):
            with self.assertRaisesRegex(ValueError, "No fue posible leer"):
                vision_service.decodificar_imagen(jpeg_simulado)

    def test_guardar_fotograma_sin_identificador_no_guarda(self):
        with patch(
            "app.services.vision_service.HistorialMovimiento"
        ) as historial:
            resultado = vision_service.guardar_fotograma_movimiento(None, object())

        self.assertEqual(resultado, ())
        self.assertEqual(vision_service._historiales_movimiento, {})
        historial.assert_not_called()

    def test_guardar_fotograma_agrega_mano_al_historial(self):
        mano = object()
        historial = MagicMock()
        historial.fotogramas = ("fotograma-1",)

        with patch(
            "app.services.vision_service.HistorialMovimiento",
            return_value=historial,
        ) as constructor:
            resultado = vision_service.guardar_fotograma_movimiento("sesion-1", mano)

        constructor.assert_called_once_with()
        historial.agregar.assert_called_once_with(mano)
        self.assertEqual(resultado, ("fotograma-1",))
        self.assertIs(vision_service._historiales_movimiento["sesion-1"], historial)

    def test_guardar_fotograma_respeta_maximo_de_secuencias(self):
        for numero in range(vision_service.MAXIMO_SECUENCIAS):
            vision_service._historiales_movimiento[f"sesion-{numero}"] = object()

        historial_nuevo = MagicMock()
        historial_nuevo.fotogramas = ("nuevo",)

        with patch(
            "app.services.vision_service.HistorialMovimiento",
            return_value=historial_nuevo,
        ):
            vision_service.guardar_fotograma_movimiento("sesion-nueva", object())

        self.assertEqual(
            len(vision_service._historiales_movimiento),
            vision_service.MAXIMO_SECUENCIAS,
        )
        self.assertNotIn("sesion-0", vision_service._historiales_movimiento)
        self.assertIn("sesion-nueva", vision_service._historiales_movimiento)

    def test_procesar_rechaza_modo_invalido_antes_de_detectar(self):
        with patch.object(vision_service._gestor_detectores, "detectar") as detector:
            with self.assertRaises(ValueError):
                vision_service.procesar_reconocimiento(object(), modo="otro")

        detector.assert_not_called()

    def test_procesar_sin_mano_devuelve_mensaje(self):
        imagen = object()
        sin_manos = SimpleNamespace(hand_landmarks=[])

        with patch.object(
            vision_service._gestor_detectores, "detectar", return_value=sin_manos
        ), patch("app.services.vision_service.reconocer_mano") as reconocer:
            resultado = vision_service.procesar_reconocimiento(imagen)

        self.assertEqual(
            resultado,
            {"letra": None, "mensaje": "No se detectó una mano"},
        )
        reconocer.assert_not_called()

    def test_procesar_estatico_no_guarda_fotogramas(self):
        imagen = object()
        mano = object()
        deteccion = SimpleNamespace(hand_landmarks=[mano])

        with patch.object(
            vision_service._gestor_detectores, "detectar", return_value=deteccion
        ), patch(
            "app.services.vision_service.guardar_fotograma_movimiento"
        ) as guardar, patch(
            "app.services.vision_service.reconocer_mano",
            return_value={"letra": "A", "requiere_movimiento": False},
        ) as reconocer:
            resultado = vision_service.procesar_reconocimiento(
                imagen, id_secuencia="sesion-1", modo="estatica"
            )

        self.assertEqual(resultado, {"letra": "A", "mensaje": None})
        guardar.assert_not_called()
        reconocer.assert_called_once_with(mano=mano, fotogramas=(), modo="estatica")

    def test_procesar_movimiento_entrega_fotogramas(self):
        imagen = object()
        mano = object()
        deteccion = SimpleNamespace(hand_landmarks=[mano])
        fotogramas = ("f1", "f2")

        with patch.object(
            vision_service._gestor_detectores, "detectar", return_value=deteccion
        ) as detector, patch(
            "app.services.vision_service.guardar_fotograma_movimiento",
            return_value=fotogramas,
        ) as guardar, patch(
            "app.services.vision_service.reconocer_mano",
            return_value={"letra": None, "requiere_movimiento": True},
        ) as reconocer:
            resultado = vision_service.procesar_reconocimiento(
                imagen, tiempo_actual=123, id_secuencia="sesion-2", modo="movimiento"
            )

        detector.assert_called_once_with(imagen, 123)
        guardar.assert_called_once_with("sesion-2", mano)
        reconocer.assert_called_once_with(
            mano=mano, fotogramas=fotogramas, modo="movimiento"
        )
        self.assertEqual(
            resultado,
            {"letra": None, "mensaje": "No se reconoció una letra"},
        )

    def test_procesar_convierte_fallo_inesperado_en_runtime_error(self):
        with patch.object(
            vision_service._gestor_detectores,
            "detectar",
            side_effect=RuntimeError("falla del detector"),
        ), patch("app.services.vision_service._logger.exception") as registrar:
            with self.assertRaisesRegex(
                RuntimeError, "No fue posible procesar el reconocimiento visual"
            ) as error:
                vision_service.procesar_reconocimiento(object())

        self.assertIsInstance(error.exception.__cause__, RuntimeError)
        registrar.assert_called_once()

    def test_procesar_imagen_base64_delega_con_parametros(self):
        imagen = object()
        respuesta = {"letra": "B", "mensaje": None}

        with patch(
            "app.services.vision_service.decodificar_imagen", return_value=imagen
        ) as decodificar, patch(
            "app.services.vision_service.procesar_reconocimiento", return_value=respuesta
        ) as procesar:
            resultado = vision_service.procesar_imagen_base64(
                "base64-simulado", id_secuencia="s3", modo="movimiento"
            )

        decodificar.assert_called_once_with("base64-simulado")
        procesar.assert_called_once_with(
            imagen, id_secuencia="s3", modo="movimiento"
        )
        self.assertIs(resultado, respuesta)

    def test_cerrar_detectores_libera_recursos_y_limpia_historiales(self):
        vision_service._historiales_movimiento["s1"] = object()

        with patch.object(vision_service._gestor_detectores, "cerrar") as cerrar:
            vision_service.cerrar_detectores()

        cerrar.assert_called_once_with()
        self.assertEqual(vision_service._historiales_movimiento, {})


if __name__ == "__main__":
    unittest.main()
