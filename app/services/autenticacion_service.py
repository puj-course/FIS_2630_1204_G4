from datetime import datetime, timedelta, timezone

from psycopg.rows import dict_row
from pwdlib import PasswordHash

from app.services.cadena_autenticacion import (
    ManejadorContrasena,
    ManejadorCuentaNoBloqueada,
    ManejadorUsuarioExistente,
    SolicitudAutenticacion,
)
from conf.database import obtener_conexion

password_hash = PasswordHash.recommended()


def obtener_usuario_por_correo(correo: str):
    with obtener_conexion() as conexion:
        with conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    id_usuario,
                    nombre,
                    correo,
                    contrasena_hash,
                    rol,
                    intentos_fallidos,
                    bloqueado_hasta
                FROM usuarios
                WHERE LOWER(correo) = LOWER(%s)
                LIMIT 1;
                """,
                (correo.strip(),)
            )

            return cursor.fetchone()


def obtener_usuario_por_id(id_usuario: int):
    with obtener_conexion() as conexion:
        with conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    id_usuario,
                    nombre,
                    correo,
                    rol
                FROM usuarios
                WHERE id_usuario = %s;
                """,
                (id_usuario,)
            )

            return cursor.fetchone()


LIMITE_INTENTOS_FALLIDOS = 5
MINUTOS_BLOQUEO = 15

def registrar_intento_fallido(id_usuario: int):
    with obtener_conexion() as conexion:
        with conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                UPDATE usuarios
                SET intentos_fallidos = intentos_fallidos + 1
                WHERE id_usuario = %s
                RETURNING intentos_fallidos;
                """,
                (id_usuario,)
            )
            intentos = cursor.fetchone()["intentos_fallidos"]

            if intentos >= LIMITE_INTENTOS_FALLIDOS:
                bloqueo_hasta = datetime.now(timezone.utc) + timedelta(
                    minutes = MINUTOS_BLOQUEO
                )

                cursor.execute(
                    """
                    UPDATE usuarios
                    SET bloqueado_hasta = %s
                    WHERE id_usuario = %s;
                    """,
                    (bloqueo_hasta, id_usuario)
                )

def reiniciar_intentos_fallidos(id_usuario: int):
    with obtener_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                UPDATE usuarios
                SET intentos_fallidos = 0,
                    bloqueado_hasta = NULL
                WHERE id_usuario = %s;
                """,
                (id_usuario,)
            )

def autenticar_usuario(correo: str, contrasena: str):
    cadena = ManejadorUsuarioExistente(obtener_usuario_por_correo)
    cadena.establecer_siguiente(
        ManejadorCuentaNoBloqueada()
    ).establecer_siguiente(
        ManejadorContrasena(
            password_hash,
            registrar_intento_fallido,
            reiniciar_intentos_fallidos
        )
    )

    return cadena.manejar(
        SolicitudAutenticacion(correo=correo, contrasena=contrasena)
    )


def generar_hash_contrasena(contrasena: str):
    return password_hash.hash(contrasena)