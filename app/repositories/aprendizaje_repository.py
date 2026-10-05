"""Consultas de base de datos para el aprendizaje automático de letras."""


def contar_aciertos_letra(
    cursor,
    id_usuario: int,
    id_letra: int,
) -> int:
    """
    Cuenta los intentos correctos de un usuario para una letra.

    Incluye los intentos de todas sus sesiones.
    Devuelve cero cuando no existen aciertos.

    Recibe un cursor configurado con dict_row. La conexión y la
    transacción son administradas por el servicio que lo utiliza.
    """

    cursor.execute(
        """
        SELECT COUNT(*) AS cantidad_aciertos
        FROM intentos_reconocimiento
        WHERE id_usuario = %s
            AND id_letra = %s
            AND es_correcto = TRUE;
        """,
        (id_usuario, id_letra),
    )

    resultado = cursor.fetchone()

    return resultado["cantidad_aciertos"]