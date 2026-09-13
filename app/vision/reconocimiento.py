from app.vision.vocales import reconocer_vocal


def reconocer_mano(mano):
    """
    Recibe los landmarks de una mano detectada
    y devuelve la vocal reconocida.
    """

    vocal = reconocer_vocal(mano)

    return {
        "letra": vocal
    }