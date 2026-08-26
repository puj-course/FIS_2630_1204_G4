from psycopg.rows import dict_row

from conf.database import obtener_conexion


def obtener_letras_registradas():
    with obtener_conexion() as conexion:
        with conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    id_letra,
                    letra,
                    descripcion,
                    ruta_imagen
                FROM letras
                WHERE activa = TRUE
                ORDER BY letra;
                """
            )

            return cursor.fetchall()