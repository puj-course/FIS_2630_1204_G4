def registrar_intento(
    cursor,
    id_resultado: int,
    id_usuario: int,
    id_sesion: int,
    id_letra: int,
    es_correcto: bool,
):
    """
    Registra el intento dentro de la transacción del resultado.

    Devuelve None si el resultado ya tiene un intento registrado.
    """

    cursor.execute(
        """
        INSERT INTO intentos_reconocimiento (
            id_resultado,
            id_usuario,
            id_sesion,
            id_letra,
            es_correcto
        )
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id_resultado) DO NOTHING
        RETURNING
            id_intento,
            id_resultado,
            id_usuario,
            id_sesion,
            id_letra,
            es_correcto,
            fecha_intento;
        """,
        (
            id_resultado,
            id_usuario,
            id_sesion,
            id_letra,
            es_correcto,
        ),
    )

    return cursor.fetchone()