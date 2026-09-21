import base64
import binascii
import logging
from threading import Lock

import cv2
import numpy as np

from app.vision.detector import DetectorMano
from app.vision.movimientos import HistorialMovimiento
from app.vision.reconocimiento import reconocer_mano

LIMITE_IMAGEN_BYTES = 5 * 1024 * 1024

_detectores: dict[bool, DetectorMano] = {}
_bloqueo_detector = Lock()
_historiales_movimiento: dict[str, HistorialMovimiento] = {}
_bloqueo_historiales = Lock()
MAXIMO_SECUENCIAS = 100
_logger = logging.getLogger(__name__)


def decodificar_imagen(imagen_base64: str):
    """Convierte una imagen Base64 al formato de OpenCV."""

    # Comprueba el tamaño del texto antes de convertirlo
    if len(imagen_base64) > 7_000_000:
        raise ValueError("La imagen codificada supera el tamaño permitido")

    # Convierte el texto en bytes
    try:
        contenido = base64.b64decode(
            imagen_base64,
            validate=True,
        )
    except (binascii.Error, ValueError) as error:
        raise ValueError(
            "El contenido enviado no es Base64 válido"
        ) from error

    # Comprueba que existan datos
    if not contenido:
        raise ValueError("La imagen está vacía")

    # Comprueba el tamaño del archivo
    if len(contenido) > LIMITE_IMAGEN_BYTES:
        raise ValueError("La imagen no puede superar 5 MiB")

    # Comprueba el formato del archivo
    es_jpeg = contenido.startswith(b"\xff\xd8\xff")
    es_png = contenido.startswith(b"\x89PNG\r\n\x1a\n")

    if not es_jpeg and not es_png:
        raise ValueError("La imagen debe tener formato JPEG o PNG")

    # Convierte los bytes en una imagen BGR
    try:
        datos = np.frombuffer(contenido, dtype=np.uint8)
        imagen = cv2.imdecode(datos, cv2.IMREAD_COLOR)
    except cv2.error as error:
        raise ValueError(
            "No fue posible leer la imagen enviada"
        ) from error

    # Comprueba que OpenCV haya leído la imagen
    if imagen is None:
        raise ValueError("No fue posible leer la imagen enviada")

    return imagen

def guardar_fotograma_movimiento(
    id_secuencia: str | None,
    mano,
):
    """
    Guarda los landmarks sin mezclar intentos diferentes.
    """

    if id_secuencia is None:
        return ()

    with _bloqueo_historiales:
        historial = _historiales_movimiento.get(
            id_secuencia
        )

        if historial is None:
            if (
                len(_historiales_movimiento)
                >= MAXIMO_SECUENCIAS
            ):
                secuencia_antigua = next(
                    iter(_historiales_movimiento)
                )

                del _historiales_movimiento[
                    secuencia_antigua
                ]

            historial = HistorialMovimiento()

            _historiales_movimiento[
                id_secuencia
            ] = historial

        historial.agregar(mano)

        return historial.fotogramas

def procesar_reconocimiento(
    imagen,
    tiempo_actual: int | None = None,
    id_secuencia: str | None = None,
) -> dict:
    """Procesa una imagen utilizando el módulo de visión."""

    # Conserva el modo video para llamadas que envían un tiempo
    modo_video = tiempo_actual is not None

    try:
        # Evita utilizar el detector simultáneamente
        with _bloqueo_detector:

            # Carga cada detector cuando se necesita por primera vez
            if modo_video not in _detectores:
                _detectores[modo_video] = DetectorMano(
                    modo_video=modo_video
                )

            detector = _detectores[modo_video]

            resultado = detector.detectar(
                imagen,
                tiempo_actual,
            )

        # Devuelve el resultado cuando no hay una mano
        if not resultado.hand_landmarks:
            return {
                "letra": None,
                "mensaje": "No se detectó una mano",
            }

        # Reconoce la vocal de la primera mano
        mano = resultado.hand_landmarks[0]
        fotogramas = guardar_fotograma_movimiento(
            id_secuencia,
            mano,
        )

        reconocimiento = reconocer_mano(
            mano,
            fotogramas,
        )

        letra = reconocimiento["letra"]

        return {
            "letra": letra,
            "mensaje": (
                None
                if letra is not None
                else "No se reconoció una letra"
            ),
        }

    except Exception as error:
        _logger.exception("Error en el reconocimiento visual")

        raise RuntimeError(
            "No fue posible procesar el reconocimiento visual"
        ) from error


def procesar_imagen_base64(
    imagen_base64: str,
    id_secuencia: str | None = None,
) -> dict:
    """Convierte y procesa la imagen recibida por el endpoint."""

    imagen = decodificar_imagen(imagen_base64)

    return procesar_reconocimiento(
        imagen,
        id_secuencia=id_secuencia,
    )


def cerrar_detectores():
    """Libera los recursos de los detectores cargados."""

    with _bloqueo_detector:
        for detector in _detectores.values():
            detector.cerrar()

        _detectores.clear()
    with _bloqueo_historiales:
        _historiales_movimiento.clear()