
import logging
import time

from app.vision.estrategia_reconocimiento import (
    EstrategiaReconocimiento,
)
from app.vision.movimientos import FotogramaMovimiento


_logger = logging.getLogger(__name__)


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


class DecoradorMedicionTiempo(DecoradorReconocimiento):
    """Mide el tiempo de ejecución del reconocimiento."""

    def reconocer(
        self,
        mano,
        fotogramas: tuple[FotogramaMovimiento, ...] = (),
    ) -> dict:
        inicio = time.perf_counter()
        estado = "error"

        try:
            resultado = super().reconocer(
                mano=mano,
                fotogramas=fotogramas,
            )

            estado = (
                "reconocida"
                if resultado.get("letra") is not None
                else "sin_coincidencia"
            )

            return resultado

        finally:
            duracion_ms = (
                time.perf_counter() - inicio
            ) * 1000

            nombre_estrategia = type(
                self._estrategia
            ).__name__

            _logger.info(
                "metrica_reconocimiento "
                "estrategia=%s "
                "duracion_ms=%.3f "
                "estado=%s",
                nombre_estrategia,
                duracion_ms,
                estado,
            )
