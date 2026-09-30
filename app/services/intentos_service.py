from psycopg.rows import dict_row

from conf.database import obtener_conexion


def registrar_intento(
    id_usuario: int,
    id_sesion: int,
    id_letra: int,
    es_correcto: bool,
):
    with obtener_conexion() as conexion:
        with conexion.cursor(row_factory=dict_row) as cursor:
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