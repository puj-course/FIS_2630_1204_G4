from app.vision.estrategia_reconocimiento import EstrategiaReconocimiento
from app.vision.letras_estaticas import reconocer_consonante_estatica
from app.vision.letras_movimiento import reconocer_letra_movimiento
from app.vision.movimientos import FotogramaMovimiento
from app.vision.vocales import reconocer_vocal


class ReconocimientoEstatico(EstrategiaReconocimiento):
    """Reconoce consonantes estáticas y, si no encuentra una, vocales."""

    def reconocer(
        self,
        mano,
        fotogramas: tuple[FotogramaMovimiento, ...] = (),
    ) -> dict:
        letra = reconocer_consonante_estatica(mano)

        if letra is None:
            letra = reconocer_vocal(mano)

        return {
            "letra": letra,
            "requiere_movimiento": False,
        }


class ReconocimientoMovimiento(EstrategiaReconocimiento):
    """Reconoce letras utilizando la mano y sus fotogramas."""

    def reconocer(
        self,
        mano,
        fotogramas: tuple[FotogramaMovimiento, ...] = (),
    ) -> dict:
        letra = reconocer_letra_movimiento(
            mano,
            fotogramas,
        )

        return {
            "letra": letra,
            "requiere_movimiento": True,
        }


class ReconocedorMano:
    """Contexto que delega el reconocimiento en una estrategia."""

    def __init__(self, estrategia: EstrategiaReconocimiento):
        self._estrategia = estrategia

    def cambiar_estrategia(
        self,
        estrategia: EstrategiaReconocimiento,
    ) -> None:
        self._estrategia = estrategia

    def reconocer(
        self,
        mano,
        fotogramas: tuple[FotogramaMovimiento, ...] = (),
    ) -> dict:
        return self._estrategia.reconocer(
            mano=mano,
            fotogramas=fotogramas,
        )


def reconocer_mano(
    mano,
    fotogramas: tuple[FotogramaMovimiento, ...] = (),
    modo: str = "estatica",
) -> dict:
    """Selecciona la estrategia conservando la entrada y salida existentes."""

    if modo not in ("estatica", "movimiento"):
        raise ValueError(
            "El modo debe ser 'estatica' o 'movimiento'"
        )

    estrategias = {
        "estatica": ReconocimientoEstatico,
        "movimiento": ReconocimientoMovimiento,
    }

    estrategia = estrategias[modo]()
    reconocedor = ReconocedorMano(estrategia)

    return reconocedor.reconocer(
        mano=mano,
        fotogramas=fotogramas,
    )