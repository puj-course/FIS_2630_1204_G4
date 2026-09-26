from datetime import datetime, timezone

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
        return None

    if not contrasena_correcta:
        return None

    return {
        "id_usuario": usuario["id_usuario"],
        "nombre": usuario["nombre"],
        "correo": usuario["correo"],
        "rol": usuario["rol"]
    }


def generar_hash_contrasena(contrasena: str):
    return password_hash.hash(contrasena)