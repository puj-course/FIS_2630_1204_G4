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

def reconocer_consonante_estatica(mano) -> str | None:
    """Reconoce las consonantes estáticas implementadas hasta ahora."""
    if len(mano) != 21:
        return None

    dedos = dedos_extendidos(mano)
    # M: índice, medio y anular extendidos hacia abajo.
    if dedos == (True, True, True, False):
        if dedos_hacia_abajo(mano, 0, 1, 2):
            return "M"

    # N: índice y medio extendidos hacia abajo.
    if dedos == (True, True, False, False):
        if (
            dedos_hacia_abajo(mano, 0, 1)
            and not pulgar_abierto(mano)
        ):
            return "N"

    # P: índice y pulgar dirigidos hacia abajo.
    if dedos == (True, False, False, False):
        if (
            dedos_hacia_abajo(mano, 0)
            and (mano[4].y - mano[2].y) / tamano_mano(mano) > 0.3
            and distancia_relativa(mano, 4, 8) > 0.6
        ):
            return "P"

    # Q: las cuatro puntas se reúnen cerca del pulgar.
    if dedos == (False, False, False, False):
        if all(
            distancia_relativa(mano, 4, punta) < 0.38
            for punta in PUNTAS
        ):
            return "Q"


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

    # K, R, T y V comparten índice y medio extendidos.
    if dedos == (True, True, False, False):
        separacion = distancia_relativa(mano, 8, 12)

        if pulgar_abierto(mano) and separacion > 0.5:
            return "K"

        if indices_cruzados(mano):
            return "R"

        if (
            separacion < 0.4
            and distancia_relativa(mano, 4, 6) < 0.7
        ):
            return "T"

        if separacion > 0.55 and not pulgar_abierto(mano):
            return "V"

    # W: índice, medio y anular extendidos y separados.
    if dedos == (True, True, True, False):
        if (
            distancia_relativa(mano, 8, 12) > 0.45
            and distancia_relativa(mano, 12, 16) > 0.45
            and not pulgar_abierto(mano)
        ):
            return "W"
    # X: índice en forma de gancho y los demás dedos doblados.
    if dedos == (False, False, False, False):
        if (
            indice_en_gancho(mano)
            and distancia_relativa(mano, 8, 5) > 0.5
        ):
            return "X"

    # Y: meñique y pulgar abiertos.
    # Se diferencia de I porque en I el pulgar queda cerrado.
    if dedos == (False, False, False, True):
        if (
            pulgar_abierto(mano)
            and distancia_relativa(mano, 4, 20) > 1.2
        ):
            return "Y"

    return None
