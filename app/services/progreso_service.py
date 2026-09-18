from psycopg.rows import dict_row

from conf.database import obtener_conexion


class UsuarioNoEncontradoError(Exception):
    pass


class LetraNoEncontradaError(Exception):
    pass

class ProgresoNoEncontradoError(Exception):
    pass

def registrar_progreso(id_usuario: int, id_letra: int):
    """
    Registra una letra como aprendida por el usuario.
    """

    with obtener_conexion() as conexion:
        with conexion.cursor(row_factory=dict_row) as cursor:

            # Verifica que el usuario exista
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

            # Verifica que la letra exista
            cursor.execute(
                """
                SELECT id_letra
                FROM letras
                WHERE id_letra = %s
                FOR KEY SHARE;
                """,
                (id_letra,),
            )

            if cursor.fetchone() is None:
                raise LetraNoEncontradaError(
                    "La letra no existe"
                )

            # Registra o actualiza la letra aprendida
            cursor.execute(
                """
                INSERT INTO progreso_usuario (
                    id_usuario,
                    id_letra,
                    dominada
                )
                VALUES (%s, %s, TRUE)
                ON CONFLICT (id_usuario, id_letra)
                DO UPDATE SET
                    dominada = TRUE,
                    fecha_actualizacion = CURRENT_TIMESTAMP
                RETURNING
                    id_progreso,
                    id_usuario,
                    id_letra,
                    cantidad_intentos,
                    cantidad_aciertos,
                    dominada,
                    fecha_ultima_practica,
                    fecha_actualizacion;
                """,
                (id_usuario, id_letra),
            )

            return cursor.fetchone()

def actualizar_estado_progreso(
    id_usuario: int,
    id_letra: int,
    dominada: bool,
):
    """
    Actualiza el estado de aprendizaje de una letra.
    """

    # Acepta únicamente los dos estados definidos
    if not isinstance(dominada, bool):
        raise ValueError(
            "El estado dominada debe ser True o False"
        )

    with obtener_conexion() as conexion:
        with conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                UPDATE progreso_usuario
                SET
                    dominada = %s,
                    fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id_usuario = %s
                    AND id_letra = %s
                RETURNING
                    id_progreso,
                    id_usuario,
                    id_letra,
                    cantidad_intentos,
                    cantidad_aciertos,
                    dominada,
                    fecha_ultima_practica,
                    fecha_actualizacion;
                """,
                (dominada, id_usuario, id_letra),
            )

            progreso = cursor.fetchone()

            if progreso is None:
                raise ProgresoNoEncontradoError(
                    "No existe progreso para este usuario y esta letra"
                )

            return progreso

def consultar_progreso_usuario(id_usuario: int):
    """
    Obtiene las letras con progreso registrado para un usuario.
    """

    with obtener_conexion() as conexion:
        with conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    p.id_progreso,
                    p.id_usuario,
                    p.id_letra,
                    l.letra,
                    p.cantidad_intentos,
                    p.cantidad_aciertos,
                    p.dominada,
                    p.fecha_ultima_practica,
                    p.fecha_actualizacion
                FROM progreso_usuario AS p
                INNER JOIN letras AS l
                    ON l.id_letra = p.id_letra
                WHERE p.id_usuario = %s
                ORDER BY l.letra, p.id_letra;
                """,
                (id_usuario,),
            )

            return cursor.fetchall()

def consultar_estado_letras_usuario(id_usuario: int):
    """
    Obtiene las letras activas y su estado de aprendizaje
    para el usuario indicado.
    """

    with obtener_conexion() as conexion:
        with conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    l.id_letra,
                    l.letra,
                    l.descripcion,
                    l.ruta_imagen,
                    CASE
                        WHEN p.dominada = TRUE THEN 'aprendida'
                        ELSE 'pendiente'
                    END AS estado
                FROM letras AS l
                LEFT JOIN progreso_usuario AS p
                    ON p.id_letra = l.id_letra
                    AND p.id_usuario = %s
                WHERE l.activa = TRUE
                ORDER BY l.letra, l.id_letra;
                """,
                (id_usuario,),
            )

            return cursor.fetchall()