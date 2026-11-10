from app.vision.vocales import (
    angulo,
    dedo_estirado,
    distancia_relativa,
    tamano_mano,
)

LETRAS_ESTATICAS_PENDIENTES = (
    "B", "C", "D", "F", "K", "L", "M", "N",
    "P", "Q", "R", "T", "V", "W", "X", "Y",
)

PUNTAS = (8, 12, 16, 20)
BASES = (5, 9, 13, 17)


def dedos_extendidos(mano) -> tuple[bool, bool, bool, bool]:
    """Indica si índice, medio, anular y meñique están extendidos."""
    return tuple(
        dedo_estirado(mano, dedo)
        for dedo in ("indice", "medio", "anular", "menique")
    )


def dedos_hacia_abajo(mano, *indices: int) -> bool:
    """Comprueba si las puntas indicadas apuntan hacia abajo."""
    escala = tamano_mano(mano)

    return all(
        (mano[PUNTAS[indice]].y - mano[BASES[indice]].y)
        / escala > 0.4
        for indice in indices
    )


def pulgar_abierto(mano) -> bool:
    """Comprueba si el pulgar está separado de la palma."""
    return (
        angulo(mano[2], mano[3], mano[4]) > 140
        and distancia_relativa(mano, 4, 5) > 0.55
        and distancia_relativa(mano, 4, 9) > 0.75
    )


def dedos_curvos(mano) -> bool:
    """Comprueba si los cuatro dedos forman un arco."""
    return all(
        75 < angulo(
            mano[base],
            mano[base + 1],
            mano[base + 2],
        ) < 155
        for base in BASES
    )


def indices_cruzados(mano) -> bool:
    """Comprueba si índice y medio se cruzan en la imagen."""

    def lado(inicio, fin, punto):
        return (
            (fin.x - inicio.x) * (punto.y - inicio.y)
            - (fin.y - inicio.y) * (punto.x - inicio.x)
        )

    inicio_indice, punta_indice = mano[5], mano[8]
    inicio_medio, punta_medio = mano[9], mano[12]

    return (
        lado(inicio_indice, punta_indice, inicio_medio)
        * lado(inicio_indice, punta_indice, punta_medio) < 0
        and lado(inicio_medio, punta_medio, inicio_indice)
        * lado(inicio_medio, punta_medio, punta_indice) < 0
    )


def indice_en_gancho(mano) -> bool:
    """Comprueba si el índice está levantado con la punta doblada."""
    return (
        angulo(mano[5], mano[6], mano[7]) > 125
        and 60 < angulo(mano[6], mano[7], mano[8]) < 140
    )


def _reconocer_tres_dedos(mano) -> str | None:
    """Prioriza M sobre W cuando índice, medio y anular están extendidos."""
    if dedos_hacia_abajo(mano, 0, 1, 2):
        return "M"

    if (
        distancia_relativa(mano, 8, 12) > 0.45
        and distancia_relativa(mano, 12, 16) > 0.45
        and not pulgar_abierto(mano)
    ):
        return "W"

    return None


def _reconocer_dos_dedos(mano) -> str | None:
    """Reconoce N, K, R, T o V con índice y medio extendidos."""
    if dedos_hacia_abajo(mano, 0, 1) and not pulgar_abierto(mano):
        return "N"

    separacion = distancia_relativa(mano, 8, 12)

    if pulgar_abierto(mano) and separacion > 0.5:
        return "K"

    if indices_cruzados(mano):
        return "R"

    if separacion < 0.4 and distancia_relativa(mano, 4, 6) < 0.7:
        return "T"

    if separacion > 0.55 and not pulgar_abierto(mano):
        return "V"

    return None


def _reconocer_indice(mano) -> str | None:
    """Reconoce P, D o L con el índice como único dedo extendido."""
    if (
        dedos_hacia_abajo(mano, 0)
        and (mano[4].y - mano[2].y) / tamano_mano(mano) > 0.3
        and distancia_relativa(mano, 4, 8) > 0.6
    ):
        return "P"

    if distancia_relativa(mano, 4, 12) < 0.4:
        return "D"

    if pulgar_abierto(mano) and distancia_relativa(mano, 4, 8) > 0.9:
        return "L"

    return None


def _reconocer_puno_cerrado(mano) -> str | None:
    """Reconoce Q o X cuando los cuatro dedos están marcados como doblados."""
    if all(
        distancia_relativa(mano, 4, punta) < 0.38
        for punta in PUNTAS
    ):
        return "Q"

    if indice_en_gancho(mano) and distancia_relativa(mano, 8, 5) > 0.5:
        return "X"

    return None


def _reconocer_cuatro_dedos(mano) -> str | None:
    """Conserva el orden y las condiciones originales de B y C."""
    if pulgar_abierto(mano):
        return None

    if all(
        distancia_relativa(mano, primera, segunda) < 0.55
        for primera, segunda in zip(PUNTAS, PUNTAS[1:])
    ):
        return "B"

    # Se conserva el alcance de C del código original: únicamente se
    # evalúa con los cuatro dedos extendidos y el pulgar cerrado.
    if dedos_curvos(mano) and distancia_relativa(mano, 4, 8) > 0.55:
        return "C"

    return None


def _reconocer_indice_menique(mano) -> str | None:
    """Reconoce F con índice y meñique extendidos y pulgar abierto."""
    if pulgar_abierto(mano):
        return "F"
    return None


def _reconocer_menique(mano) -> str | None:
    """Reconoce Y con meñique extendido y pulgar abierto."""
    if pulgar_abierto(mano) and distancia_relativa(mano, 4, 20) > 1.2:
        return "Y"
    return None


_RECONOCEDORES_POR_DEDOS = {
    (True, True, True, False): _reconocer_tres_dedos,
    (True, True, False, False): _reconocer_dos_dedos,
    (True, False, False, False): _reconocer_indice,
    (False, False, False, False): _reconocer_puno_cerrado,
    (True, True, True, True): _reconocer_cuatro_dedos,
    (True, False, False, True): _reconocer_indice_menique,
    (False, False, False, True): _reconocer_menique,
}


def reconocer_consonante_estatica(mano) -> str | None:
    """Reconoce las consonantes estáticas implementadas hasta ahora."""
    if len(mano) != 21:
        return None

    dedos = dedos_extendidos(mano)
    reconocedor = _RECONOCEDORES_POR_DEDOS.get(dedos)

    if reconocedor is None:
        return None

    return reconocedor(mano)