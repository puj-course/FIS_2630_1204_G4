from psycopg.rows import dict_row

from conf.database import obtener_conexion


class SesionNoEncontradaError(Exception):
    pass


class LetraNoEncontradaError(Exception):
    pass


class UsuarioSesionError(Exception):
    pass



def registrar_resultado(
    id_usuario: int,
    id_sesion: int,
    id_letra_objetivo: int,
    id_letra_detectada: int,
    confianza: float,
):
    """
    Registra un resultado obtenido durante una sesión.
    """

    with obtener_conexion() as conexion:
        with conexion.cursor(row_factory=dict_row) as cursor:

            # Verifica que la sesión exista
            cursor.execute(
                """
                SELECT id_usuario
                FROM sesiones_reconocimiento
                WHERE id_sesion = %s;
                """,
                (id_sesion,),
            )

            sesion = cursor.fetchone()

            if sesion is None:
                raise SesionNoEncontradaError(
                    "La sesión no existe"
                )


            # Verifica que la sesión pertenezca al usuario
            if sesion["id_usuario"] != id_usuario:
                raise UsuarioSesionError(
                    "La sesión no pertenece al usuario"
                )


            # Verifica que las letras existan
            cursor.execute(
                """
                SELECT id_letra
                FROM letras
                WHERE id_letra IN (%s, %s);
                """,
                (
                    id_letra_objetivo,
                    id_letra_detectada,
                ),
            )

            letras = cursor.fetchall()

            if len(letras) != 2:
                raise LetraNoEncontradaError(
                    "Alguna letra no existe"
                )


            # Determina si fue correcto
            es_correcto = (
                id_letra_objetivo ==
                id_letra_detectada
            )


            # Guarda el resultado
            cursor.execute(
                """
                INSERT INTO resultados_reconocimiento (
                    id_sesion,
                    id_letra_objetivo,
                    id_letra_detectada,
                    confianza,
                    es_correcto
                )
                VALUES (%s, %s, %s, %s, %s)

                RETURNING
                    id_resultado,
                    id_sesion,
                    id_letra_objetivo,
                    id_letra_detectada,
                    confianza,
                    es_correcto,
                    fecha_resultado;
                """,
                (
                    id_sesion,
                    id_letra_objetivo,
                    id_letra_detectada,
                    confianza,
                    es_correcto,
                ),
            )

            return cursor.fetchone()