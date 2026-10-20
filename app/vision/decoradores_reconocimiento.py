
from app.vision.estrategia_reconocimiento import (
    EstrategiaReconocimiento,
)
from app.vision.movimientos import FotogramaMovimiento


class DecoradorReconocimiento(EstrategiaReconocimiento):
    """Clase base para extender las estrategias de reconocimiento."""

    def __init__(self, estrategia: EstrategiaReconocimiento):
        self._estrategia = estrategia

    def reconocer(
        self,
        mano,
        fotogramas: tuple[FotogramaMovimiento, ...] = (),
    ) -> dict:
        """Delega el reconocimiento en la estrategia original."""

        return self._estrategia.reconocer(
            mano=mano,
            fotogramas=fotogramas,
        )
