from collections import deque
from dataclasses import dataclass
import math


LETRAS_CON_MOVIMIENTO = (
    "G",
    "H",
    "J",
    "Ñ",
    "S",
    "Z",
)

CANTIDAD_LANDMARKS = 21
MAXIMO_FOTOGRAMAS = 20


@dataclass(frozen=True)
class PuntoMovimiento:
    """
    Representa la posición tridimensional de un landmark.
    """

    x: float
    y: float
    z: float


@dataclass(frozen=True)
class FotogramaMovimiento:
    """
    Conserva los landmarks detectados en un fotograma.
    """

    puntos: tuple[PuntoMovimiento, ...]
    escala_mano: float

    @classmethod
    def desde_mano(cls, mano):
        if len(mano) != CANTIDAD_LANDMARKS:
            raise ValueError(
                "La mano debe contener 21 landmarks"
            )

        puntos = tuple(
            PuntoMovimiento(
                x=float(punto.x),
                y=float(punto.y),
                z=float(punto.z),
            )
            for punto in mano
        )

        muñeca = puntos[0]
        base_medio = puntos[9]

        escala_mano = math.sqrt(
            (muñeca.x - base_medio.x) ** 2
            + (muñeca.y - base_medio.y) ** 2
            + (muñeca.z - base_medio.z) ** 2
        )

        return cls(
            puntos=puntos,
            escala_mano=max(escala_mano, 0.000001),
        )

    def obtener_punto(self, indice: int) -> PuntoMovimiento:
        return self.puntos[indice]


class HistorialMovimiento:
    """
    Mantiene una cantidad limitada de posiciones consecutivas.
    """

    def __init__(
        self,
        maximo_fotogramas: int = MAXIMO_FOTOGRAMAS,
    ):
        if maximo_fotogramas < 2:
            raise ValueError(
                "El historial requiere al menos dos fotogramas"
            )

        self._fotogramas = deque(
            maxlen=maximo_fotogramas
        )

    @property
    def fotogramas(self) -> tuple[FotogramaMovimiento, ...]:
        return tuple(self._fotogramas)

    def agregar(self, mano) -> None:
        self._fotogramas.append(
            FotogramaMovimiento.desde_mano(mano)
        )

    def limpiar(self) -> None:
        self._fotogramas.clear()

    def __len__(self) -> int:
        return len(self._fotogramas)