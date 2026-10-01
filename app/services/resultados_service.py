from psycopg.rows import dict_row

from app.services.intentos_service import registrar_intento
from conf.database import obtener_conexion


class SesionNoEncontradaError(Exception):
    pass


class SesionNoActivaError(Exception):
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
    """Registra el resultado y su intento en una sesión activa."""

    with obtener_conexion() as conexion:
        with conexion.cursor(row_factory=dict_row) as cursor:
            # Bloquea la sesión hasta terminar la transacción.
            cursor.execute(
                """
                SELECT id_usuario, estado
                FROM sesiones_reconocimiento
                WHERE id_sesion = %s
                FOR UPDATE;
                """,
                (id_sesion,),
            )

            sesion = cursor.fetchone()

            if sesion is None:
                raise SesionNoEncontradaError(
                    "La sesión no existe"
                )

            if sesion["id_usuario"] != id_usuario:
                raise UsuarioSesionError(
                    "La sesión no pertenece al usuario"
                )

            if sesion["estado"] != "activa":
                raise SesionNoActivaError(
                    "Solo se pueden registrar resultados en sesiones activas"
                )

            # Verifica que ambas letras existan.
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

            ids_encontrados = {
                letra["id_letra"]
                for letra in letras
            }

            ids_solicitados = {
                id_letra_objetivo,
                id_letra_detectada,
            }

            if not ids_solicitados.issubset(ids_encontrados):
                raise LetraNoEncontradaError(
                    "Alguna letra no existe"
                )

            es_correcto = (
                id_letra_objetivo == id_letra_detectada
            )

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

            resultado = cursor.fetchone()

            # Ambos registros utilizan la misma transacción.
            registrar_intento(
                cursor=cursor,
                id_resultado=resultado["id_resultado"],
                id_usuario=id_usuario,
                id_sesion=id_sesion,
                id_letra=id_letra_objetivo,
                es_correcto=es_correcto,
            )

            return resultado


def consultar_resultados_sesion(
    id_usuario: int,
    id_sesion: int,
):
    """Consulta los resultados propios sin restringir el estado de sesión."""

    with obtener_conexion() as conexion:
        with conexion.cursor(row_factory=dict_row) as cursor:
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

            if sesion["id_usuario"] != id_usuario:
                raise UsuarioSesionError(
                    "La sesión no pertenece al usuario"
                )

            cursor.execute(
                """
                SELECT
                    r.id_resultado,
                    r.id_sesion,
                    r.id_letra_objetivo,
                    r.id_letra_detectada,
                    r.confianza,
                    r.es_correcto,
                    r.fecha_resultado
                FROM resultados_reconocimiento AS r
                INNER JOIN sesiones_reconocimiento AS s
                    ON s.id_sesion = r.id_sesion
                WHERE r.id_sesion = %s
                    AND s.id_usuario = %s
                ORDER BY
                    r.fecha_resultado ASC,
                    r.id_resultado ASC;
                """,
                (id_sesion, id_usuario),
            )

            return cursor.fetchall()