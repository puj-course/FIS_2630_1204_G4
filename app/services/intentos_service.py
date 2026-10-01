from psycopg.rows import dict_row

from conf.database import obtener_conexion


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


def consultar_intentos_usuario(
    id_usuario: int,
    id_letra: int | None = None,
    id_sesion: int | None = None,
) -> list[dict]:
    """
    Consulta los intentos de un usuario.

    Permite filtrar por letra objetivo, sesión o ambos.
    Devuelve los intentos del más reciente al más antiguo.
    Si no hay coincidencias, devuelve una lista vacía.
    """

    consulta = """
        SELECT
            id_intento,
            id_resultado,
            id_usuario,
            id_sesion,
            id_letra,
            es_correcto,
            fecha_intento
        FROM intentos_reconocimiento
        WHERE id_usuario = %s
    """

    parametros = [id_usuario]

    if id_letra is not None:
        consulta += " AND id_letra = %s"
        parametros.append(id_letra)

    if id_sesion is not None:
        consulta += " AND id_sesion = %s"
        parametros.append(id_sesion)

    consulta += """
        ORDER BY
            fecha_intento DESC,
            id_intento DESC;
    """

    with obtener_conexion() as conexion:
        with conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                consulta,
                tuple(parametros),
            )

            return cursor.fetchall()