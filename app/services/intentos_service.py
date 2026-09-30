def registrar_intento(
    cursor,
    id_usuario: int,
    id_sesion: int,
    id_letra: int,
    es_correcto: bool,
):
    """Registra el intento usando la transacción del resultado."""

    cursor.execute(
        """
        INSERT INTO intentos_reconocimiento (
            id_usuario,
            id_sesion,
            id_letra,
            es_correcto
        )
        VALUES (%s, %s, %s, %s)
        RETURNING
            id_intento,
            id_usuario,
            id_sesion,
            id_letra,
            es_correcto,
            fecha_intento;
        """,
        (
            id_usuario,
            id_sesion,
            id_letra,
            es_correcto,
        ),
    )

    return cursor.fetchone()