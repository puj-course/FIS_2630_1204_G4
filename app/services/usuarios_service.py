from psycopg.errors import UniqueViolation
from psycopg.rows import dict_row

from app.services.autenticacion_service import generar_hash_contrasena
from conf.database import obtener_conexion


class CorreoYaRegistradoError(Exception):
    pass


def crear_usuario(
    nombre: str,
    correo: str,
    contrasena: str,
    rol: str
):
    contrasena_hash = generar_hash_contrasena(contrasena)

    try:
        with obtener_conexion() as conexion:
            with conexion.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    INSERT INTO usuarios (
                        nombre,
                        correo,
                        contrasena_hash,
                        rol
                    )
                    VALUES (%s, %s, %s, %s)
                    RETURNING
                        id_usuario,
                        nombre,
                        correo,
                        rol;
                    """,
                    (
                        nombre.strip(),
                        correo.strip().lower(),
                        contrasena_hash,
                        rol
                    )
                )

                return cursor.fetchone()

    except UniqueViolation as error:
        raise CorreoYaRegistradoError(
            "El correo ya se encuentra registrado"
        ) from error


def listar_usuarios(buscar: str | None = None):
    with obtener_conexion() as conexion:
        with conexion.cursor(row_factory=dict_row) as cursor:
            if buscar:
                cursor.execute(
                    """
                    SELECT
                        id_usuario,
                        nombre,
                        correo,
                        rol,
                        fecha_creacion
                    FROM usuarios
                    WHERE nombre ILIKE %s OR correo ILIKE %s
                    ORDER BY nombre;
    
                    """,
                    (f"%{buscar}%", f"%{buscar}%")
                )
            else:
                cursor.execute(
                    """
                    SELECT
                        id_usuario,
                        nombre,
                        correo,
                        rol,
                        fecha_creacion
                    FROM usuarios
                    ORDER BY nombre;
                    """
                )

            return cursor.fetchall()

def cambiar_rol(id_usuario: int, nuevo_rol: str):
    with obtener_conexion() as conexion:
        with conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                UPDATE usuarios
                SET rol = %s
                WHERE id_usuario = %s
                RETURNING
                    id_usuario,
                    nombre,
                    correo,
                    rol;
                """,
                (nuevo_rol, id_usuario)
            )

            return cursor.fetchone()