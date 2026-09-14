from app.vision.detector import DetectorMano
from app.vision.reconocimiento import reconocer_mano


# Instancia única del detector para reutilizar el modelo cargado
_detector_mano = DetectorMano()


def procesar_reconocimiento(
    imagen,
    tiempo_actual: int
) -> dict:
    """
    Procesa una imagen utilizando el módulo de visión.
    """

    try:
        resultado = _detector_mano.detectar(
            imagen,
            tiempo_actual
        )

        if not resultado.hand_landmarks:
            return {
                "letra": None,
                "mensaje": "No se detectó una mano"
            }

        mano = resultado.hand_landmarks[0]

        return reconocer_mano(mano)

    except Exception as error:
        raise RuntimeError(
            "No fue posible procesar el reconocimiento visual"
        ) from error