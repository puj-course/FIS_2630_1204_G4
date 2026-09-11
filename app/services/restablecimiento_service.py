from psycopg.rows import dict_row

from app.services.autenticacion_service import generar_hash_contrasena
from app.services.recuperacion_service import generar_hash_token
from conf.database import obtener_conexion


class SolicitudRecuperacionInvalidaError(Exception):
    pass


def restablecer_contrasena(token: str, nueva_contrasena: str) -> None:
    token_hash = generar_hash_token(token)

    with obtener_conexion() as conexion:
        with conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT id_recuperacion, id_usuario
                FROM recuperaciones_contrasena
                WHERE token_hash = %s
                    AND fecha_uso IS NULL
                    AND fecha_invalidacion IS NULL
                    AND fecha_expiracion > statement_timestamp();
                """,
                (token_hash,)
            )
            solicitud = cursor.fetchone()
            if solicitud is None:
                raise SolicitudRecuperacionInvalidaError()

            # Mismo orden de bloqueo que al crear solicitudes: primero usuario.
            cursor.execute(
                """
                SELECT id_usuario FROM usuarios
                WHERE id_usuario = %s
                FOR UPDATE;
                """,
                (solicitud["id_usuario"],)
            )
            if cursor.fetchone() is None:
                raise SolicitudRecuperacionInvalidaError()

            contrasena_hash = generar_hash_contrasena(nueva_contrasena)

            # Revalidar después del bloqueo y del cálculo del hash: otro proceso
            # pudo usar o invalidar el token, o este pudo vencer mientras tanto.
            cursor.execute(
                """
                UPDATE recuperaciones_contrasena
                SET fecha_uso = statement_timestamp()
                WHERE id_recuperacion = %s
                    AND id_usuario = %s
                    AND token_hash = %s
                    AND fecha_uso IS NULL
                    AND fecha_invalidacion IS NULL
                    AND fecha_expiracion > statement_timestamp()
                RETURNING id_recuperacion;
                """,
                (
                    solicitud["id_recuperacion"],
                    solicitud["id_usuario"],
                    token_hash
                )
            )
            if cursor.fetchone() is None:
                raise SolicitudRecuperacionInvalidaError()

            cursor.execute(
                """
                UPDATE usuarios
                SET contrasena_hash = %s
                WHERE id_usuario = %s
                RETURNING id_usuario;
                """,
                (contrasena_hash, solicitud["id_usuario"])
            )
            if cursor.fetchone() is None:
                raise RuntimeError("No fue posible actualizar la contraseña")

            cursor.execute(
                """
                UPDATE recuperaciones_contrasena
                SET fecha_invalidacion = statement_timestamp()
                WHERE id_usuario = %s
                    AND fecha_uso IS NULL
                    AND fecha_invalidacion IS NULL;
                """,
                (solicitud["id_usuario"],)
            )
    # El contexto confirma ambos cambios juntos; ante una excepción los revierte.
