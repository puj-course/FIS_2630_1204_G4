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