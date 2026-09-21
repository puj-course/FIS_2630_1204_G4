import math
from collections import deque
from dataclasses import dataclass
from typing import Literal

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

DireccionMovimiento = Literal[
    "izquierda",
    "derecha",
    "arriba",
    "abajo",
    "quieto",
]


@dataclass(frozen=True)
class ResumenTrayectoria:
    desplazamiento_x: float
    desplazamiento_y: float
    recorrido_total: float
    rango_x: float
    rango_y: float
    cambios_direccion_x: int
    cambios_direccion_y: int


def obtener_trayectoria(
    fotogramas: tuple[FotogramaMovimiento, ...],
    indice_punto: int,
) -> tuple[PuntoMovimiento, ...]:
    """
    Obtiene la trayectoria normalizada de un punto de la mano.
    """

    if not 0 <= indice_punto < CANTIDAD_LANDMARKS:
        raise ValueError("El índice del punto no es válido")

    if not fotogramas:
        return ()

    punto_inicial = fotogramas[0].obtener_punto(indice_punto)

    trayectoria = []

    for fotograma in fotogramas:
        punto = fotograma.obtener_punto(indice_punto)
        escala = max(fotograma.escala_mano, 1e-6)

        trayectoria.append(
            PuntoMovimiento(
                x=(punto.x - punto_inicial.x) / escala,
                y=(punto.y - punto_inicial.y) / escala,
                z=(punto.z - punto_inicial.z) / escala,
            )
        )

    return tuple(trayectoria)


def contar_cambios_direccion(
    valores: tuple[float, ...],
    umbral: float = 0.08,
) -> int:
    """
    Cuenta cambios significativos de dirección en un eje.
    """

    direccion_anterior = 0
    cambios = 0

    for anterior, actual in zip(valores, valores[1:]):
        diferencia = actual - anterior

        if abs(diferencia) < umbral:
            continue

        direccion_actual = 1 if diferencia > 0 else -1

        if (
            direccion_anterior != 0
            and direccion_actual != direccion_anterior
        ):
            cambios += 1

        direccion_anterior = direccion_actual

    return cambios


def analizar_trayectoria(
    trayectoria: tuple[PuntoMovimiento, ...],
) -> ResumenTrayectoria:
    """
    Resume el desplazamiento y recorrido de una trayectoria.
    """

    if len(trayectoria) < 2:
        return ResumenTrayectoria(
            desplazamiento_x=0.0,
            desplazamiento_y=0.0,
            recorrido_total=0.0,
            rango_x=0.0,
            rango_y=0.0,
            cambios_direccion_x=0,
            cambios_direccion_y=0,
        )

    posiciones_x = tuple(punto.x for punto in trayectoria)
    posiciones_y = tuple(punto.y for punto in trayectoria)

    recorrido_total = sum(
        math.hypot(
            actual.x - anterior.x,
            actual.y - anterior.y,
        )
        for anterior, actual in zip(
            trayectoria,
            trayectoria[1:],
        )
    )

    return ResumenTrayectoria(
        desplazamiento_x=(
            trayectoria[-1].x - trayectoria[0].x
        ),
        desplazamiento_y=(
            trayectoria[-1].y - trayectoria[0].y
        ),
        recorrido_total=recorrido_total,
        rango_x=max(posiciones_x) - min(posiciones_x),
        rango_y=max(posiciones_y) - min(posiciones_y),
        cambios_direccion_x=contar_cambios_direccion(
            posiciones_x
        ),
        cambios_direccion_y=contar_cambios_direccion(
            posiciones_y
        ),
    )


def obtener_direccion_principal(
    resumen: ResumenTrayectoria,
    umbral: float = 0.25,
) -> DireccionMovimiento:
    """
    Determina la dirección predominante del movimiento.
    """

    desplazamiento_x = resumen.desplazamiento_x
    desplazamiento_y = resumen.desplazamiento_y

    if (
        abs(desplazamiento_x) < umbral
        and abs(desplazamiento_y) < umbral
    ):
        return "quieto"

    if abs(desplazamiento_x) >= abs(desplazamiento_y):
        return (
            "derecha"
            if desplazamiento_x > 0
            else "izquierda"
        )

    return "abajo" if desplazamiento_y > 0 else "arriba"