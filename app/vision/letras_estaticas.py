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


def reconocer_consonante_estatica(mano) -> str | None:
    """Reconoce las consonantes estáticas implementadas hasta ahora."""
    if len(mano) != 21:
        return None

    dedos = dedos_extendidos(mano)

    # B: cuatro dedos extendidos y juntos; pulgar sobre la palma.
    if dedos == (True, True, True, True) and not pulgar_abierto(mano):
        if all(
            distancia_relativa(mano, primera, segunda) < 0.55
            for primera, segunda in zip(PUNTAS, PUNTAS[1:])
        ):
            return "B"

    # C: dedos curvos y espacio entre índice y pulgar.
        if (
            dedos_curvos(mano)
            and distancia_relativa(mano, 4, 8) > 0.55
        ):
            return "C"

        # D: índice extendido; pulgar cerca de la punta del medio.
        if dedos == (True, False, False, False):
            if distancia_relativa(mano, 4, 12) < 0.4:
                return "D"
    # D: índice extendido; pulgar cerca de la punta del medio.
    if dedos == (True, False, False, False):
        if distancia_relativa(mano, 4, 12) < 0.4:
            return "D"

        # L: índice extendido y pulgar abierto hacia un lado.
        if (
            pulgar_abierto(mano)
            and distancia_relativa(mano, 4, 8) > 0.9
        ):
            return "L"

    # F: índice y meñique extendidos, con el pulgar abierto.
    # En U el pulgar permanece sobre la palma.
    if dedos == (True, False, False, True):
        if pulgar_abierto(mano):
            return "F"

    # K: índice y medio separados, con el pulgar abierto.
    if dedos == (True, True, False, False):
        if (
            pulgar_abierto(mano)
            and distancia_relativa(mano, 8, 12) > 0.5
        ):
            return "K"

    return None
