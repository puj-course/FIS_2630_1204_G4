from abc import ABC, abstractmethod

from app.vision.movimientos import FotogramaMovimiento


class EstrategiaReconocimiento(ABC):
    """Contrato común para los algoritmos de reconocimiento."""

    @abstractmethod
    def reconocer(
        self,
        mano,
        fotogramas: tuple[FotogramaMovimiento, ...] = (),
    ) -> dict:
        """Devuelve la letra reconocida y si requiere movimiento."""
        raise NotImplementedError