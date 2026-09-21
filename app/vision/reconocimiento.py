from app.vision.letras_movimiento import (
    reconocer_letra_movimiento,
)
from app.vision.movimientos import FotogramaMovimiento
from app.vision.vocales import reconocer_vocal


def reconocer_mano(
    mano,
    fotogramas: tuple[FotogramaMovimiento, ...] = (),
    modo: str = "estatica",
):
    """
    Reconoce la letra usando únicamente la lógica del modo elegido.
    """

    if modo == "movimiento":
        letra = reconocer_letra_movimiento(
            mano,
            fotogramas,
        )

        return {
            "letra": letra,
            "requiere_movimiento": True,
        }

    if modo == "estatica":
        letra = reconocer_vocal(mano)

        return {
            "letra": letra,
            "requiere_movimiento": False,
        }

    raise ValueError(
        "El modo debe ser 'estatica' o 'movimiento'"
    )