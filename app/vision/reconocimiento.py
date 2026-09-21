from app.vision.letras_movimiento import (
    reconocer_letra_movimiento,
)
from app.vision.movimientos import FotogramaMovimiento
from app.vision.vocales import reconocer_vocal


def reconocer_mano(
    mano,
    fotogramas: tuple[FotogramaMovimiento, ...] = (),
):
    """
    Reconoce primero las letras con movimiento y después
    las letras estáticas.
    """

    letra_movimiento = reconocer_letra_movimiento(
        mano,
        fotogramas,
    )

    if letra_movimiento is not None:
        return {
            "letra": letra_movimiento,
            "requiere_movimiento": True,
        }

    letra_estatica = reconocer_vocal(mano)

    return {
        "letra": letra_estatica,
        "requiere_movimiento": False,
    }