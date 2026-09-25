from psycopg.rows import dict_row

from conf.database import obtener_conexion


class UsuarioNoEncontradoError(Exception):
    pass


class SesionNoEncontradaError(Exception):
    pass


class EstadoSesionError(Exception):
    pass


def crear_sesion(id_usuario: int):
    """Crea una sesión activa para un usuario existente."""

    with obtener_conexion() as conexion:
        with conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT id_usuario
                FROM usuarios
                WHERE id_usuario = %s
                FOR KEY SHARE;
                """,
                (id_usuario,),
            )

            if cursor.fetchone() is None:
                raise UsuarioNoEncontradoError(
                    "El usuario no existe"
                )

            cursor.execute(
                """
                INSERT INTO sesiones_reconocimiento (
                    id_usuario,
                    estado
                )
                VALUES (%s, 'activa')
                RETURNING
                    id_sesion,
                    id_usuario,
                    fecha_inicio,
                    fecha_fin,
                    estado;
                """,
                (id_usuario,),
            )

            return cursor.fetchone()


def consultar_sesion(id_usuario: int, id_sesion: int):
    """Consulta una sesión perteneciente al usuario."""

    with obtener_conexion() as conexion:
        with conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    id_sesion,
                    id_usuario,
                    fecha_inicio,
                    fecha_fin,
                    estado
                FROM sesiones_reconocimiento
                WHERE id_sesion = %s
                    AND id_usuario = %s;
                """,
                (id_sesion, id_usuario),
            )

            sesion = cursor.fetchone()

            if sesion is None:
                raise SesionNoEncontradaError(
                    "No se encontró la sesión para este usuario"
                )

            return sesion


def finalizar_sesion(id_usuario: int, id_sesion: int):
    """Finaliza una sesión activa perteneciente al usuario."""

    with obtener_conexion() as conexion:
        with conexion.cursor(row_factory=dict_row) as cursor:
            # Bloquea la sesión durante la operación para evitar
            # que dos solicitudes cambien su estado simultáneamente.
            cursor.execute(
                """
                SELECT
                    id_sesion,
                    id_usuario,
                    fecha_inicio,
                    fecha_fin,
                    estado
                FROM sesiones_reconocimiento
                WHERE id_sesion = %s
                    AND id_usuario = %s
                FOR UPDATE;
                """,
                (id_sesion, id_usuario),
            )

            sesion = cursor.fetchone()

            if sesion is None:
                raise SesionNoEncontradaError(
                    "No se encontró la sesión para este usuario"
                )

            # Repetir la finalización conserva la fecha original.
            if sesion["estado"] == "finalizada":
                return sesion

            if sesion["estado"] != "activa":
                raise EstadoSesionError(
                    "Solo se pueden finalizar sesiones activas"
                )

            cursor.execute(
                """
                UPDATE sesiones_reconocimiento
                SET
                    estado = 'finalizada',
                    fecha_fin = GREATEST(
                        CURRENT_TIMESTAMP,
                        fecha_inicio
                    )
                WHERE id_sesion = %s
                    AND id_usuario = %s
                    AND estado = 'activa'
                RETURNING
                    id_sesion,
                    id_usuario,
                    fecha_inicio,
                    fecha_fin,
                    estado;
                """,
                (id_sesion, id_usuario),
            )

            return cursor.fetchone()