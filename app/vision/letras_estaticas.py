from app.vision.vocales import (
    dedo_estirado,
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