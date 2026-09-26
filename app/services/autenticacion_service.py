from datetime import datetime, timedelta, timezone

from psycopg.rows import dict_row
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError

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

class CuentaBloqueadaError(Exception):
    pass


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
    usuario = obtener_usuario_por_correo(correo)

    if usuario is None:
        return None
    
    if usuario["bloqueado_hasta"] is not None:
        if usuario["bloqueado_hasta"] > datetime.now(timezone.utc):
            raise CuentaBloqueadaError(
                "La cuenta está bloqueada temporalmente"
            )
        
    try:
        contrasena_correcta = password_hash.verify(
            contrasena,
            usuario["contrasena_hash"]
        )
    except UnknownHashError:
        registrar_intento_fallido(usuario["id_usuario"])
        return None

    if not contrasena_correcta:
        registrar_intento_fallido(usuario["id_usuario"])
        return None

    reiniciar_intentos_fallidos(usuario["id_usuario"])

    return {
        "id_usuario": usuario["id_usuario"],
        "nombre": usuario["nombre"],
        "correo": usuario["correo"],
        "rol": usuario["rol"]
    }


def generar_hash_contrasena(contrasena: str):
    return password_hash.hash(contrasena)