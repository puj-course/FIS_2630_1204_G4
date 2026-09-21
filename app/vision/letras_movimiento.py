from app.vision.movimientos import (
    FotogramaMovimiento,
    analizar_trayectoria,
    obtener_trayectoria,
)
from app.vision.vocales import (
    anular_estirado,
    indice_estirado,
    medio_estirado,
    menique_estirado,
    pulgar_estirado,
)


MINIMO_FOTOGRAMAS = 6

PUNTO_MUNECA = 0
PUNTA_INDICE = 8
PUNTA_MENIQUE = 20


def reconocer_letra_movimiento(
    mano,
    fotogramas: tuple[FotogramaMovimiento, ...],
) -> str | None:
    """
    Reconoce letras dinámicas mediante la configuración
    de los dedos y la trayectoria de la mano.
    """

    if len(fotogramas) < MINIMO_FOTOGRAMAS:
        return None

    indice = indice_estirado(mano)
    medio = medio_estirado(mano)
    anular = anular_estirado(mano)
    menique = menique_estirado(mano)
    pulgar = pulgar_estirado(mano)

    resumen_muneca = analizar_trayectoria(
        obtener_trayectoria(
            fotogramas,
            PUNTO_MUNECA,
        )
    )

    resumen_indice = analizar_trayectoria(
        obtener_trayectoria(
            fotogramas,
            PUNTA_INDICE,
        )
    )

    resumen_menique = analizar_trayectoria(
        obtener_trayectoria(
            fotogramas,
            PUNTA_MENIQUE,
        )
    )

    if (
        indice
        and not medio
        and not anular
        and not menique
        and resumen_indice.cambios_direccion_x >= 2
        and resumen_indice.rango_x >= 0.7
        and resumen_indice.rango_y >= 0.35
    ):
        return "Z"

    if (
        menique
        and not indice
        and not medio
        and not anular
        and resumen_menique.rango_y >= 0.6
        and resumen_menique.rango_x >= 0.25
        and resumen_menique.cambios_direccion_x >= 1
    ):
        return "J"

    if (
        indice
        and medio
        and not anular
        and not menique
        and resumen_muneca.rango_x >= 0.55
        and resumen_muneca.rango_y <= 0.45
    ):
        return "H"

    if (
        indice
        and pulgar
        and not medio
        and not anular
        and not menique
        and resumen_muneca.rango_x >= 0.55
        and resumen_muneca.rango_y <= 0.45
    ):
        return "G"

    dedos_principales_doblados = (
        not indice
        and not medio
        and not anular
        and not menique
    )

    if (
        dedos_principales_doblados
        and resumen_muneca.cambios_direccion_x >= 2
        and resumen_muneca.rango_x >= 0.45
        and resumen_muneca.rango_y >= 0.45
        and resumen_muneca.recorrido_total >= 1.2
    ):
        return "S"

    if (
        dedos_principales_doblados
        and resumen_muneca.cambios_direccion_x >= 1
        and resumen_muneca.rango_x >= 0.45
        and resumen_muneca.rango_y <= 0.45
    ):
        return "Ñ"

    return None
