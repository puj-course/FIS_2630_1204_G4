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


def registrar_aprendizaje(
    cursor,
    id_usuario: int,
    id_letra: int,
) -> dict | None:
    """
    Marca una letra como aprendida si todavía no lo está.

    Crea el progreso cuando no existe o actualiza uno pendiente.
    Devuelve el registro creado o actualizado.

    Si la letra ya estaba aprendida, no modifica sus datos y
    devuelve None.

    El servicio debe verificar el mínimo de aciertos antes de llamar
    a esta función. El cursor debe estar configurado con dict_row.
    """

    cursor.execute(
        """
        INSERT INTO progreso_usuario (
            id_usuario,
            id_letra,
            dominada
        )
        VALUES (%s, %s, TRUE)
        ON CONFLICT (id_usuario, id_letra)
        DO UPDATE SET
            dominada = TRUE,
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE progreso_usuario.dominada = FALSE
        RETURNING
            id_progreso,
            id_usuario,
            id_letra,
            cantidad_intentos,
            cantidad_aciertos,
            dominada,
            fecha_ultima_practica,
            fecha_actualizacion;
        """,
        (id_usuario, id_letra),
    )

    return cursor.fetchone()