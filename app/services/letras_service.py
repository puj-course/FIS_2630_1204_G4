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

def obtener_letra_por_id(id_letra):
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
                WHERE id_letra = %s;
                """,
                (id_letra,)
            )

            return cursor.fetchone()

def actualizar_informacion_letra(
    id_letra: int,
    cambios: dict
):
    descripcion_enviada = "descripcion" in cambios
    ruta_imagen_enviada = "ruta_imagen" in cambios

    with obtener_conexion() as conexion:
        with conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                UPDATE letras
                SET
                    descripcion = CASE
                        WHEN %s THEN %s
                        ELSE descripcion
                    END,
                    ruta_imagen = CASE
                        WHEN %s THEN %s
                        ELSE ruta_imagen
                    END,
                    fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id_letra = %s
                RETURNING
                    id_letra,
                    letra,
                    descripcion,
                    ruta_imagen;
                """,
                (
                    descripcion_enviada,
                    cambios.get("descripcion"),
                    ruta_imagen_enviada,
                    cambios.get("ruta_imagen"),
                    id_letra
                )
            )

            return cursor.fetchone()