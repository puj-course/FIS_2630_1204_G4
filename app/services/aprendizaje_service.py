"""Evaluación del aprendizaje a partir de intentos correctos almacenados."""

from psycopg.rows import dict_row

from app.repositories.aprendizaje_repository import (
    contar_aciertos_letra,
    registrar_aprendizaje,
)
from conf.config import obtener_minimo_aciertos
from conf.database import obtener_conexion


def evaluar_aprendizaje(
    id_usuario: int,
    id_letra: int,
) -> dict | None:
    """
    Evalúa el aprendizaje de una letra para un usuario.

    Recibe los identificadores del usuario y de la letra previamente
    validados por el flujo que registra el reconocimiento.

    Devuelve el progreso creado o actualizado cuando se alcanza
    el mínimo de aciertos y la letra todavía no estaba aprendida.

    Devuelve None si faltan aciertos o el progreso ya estaba aprendido.
    No elimina aprendizajes previos al cambiar el mínimo configurado.

    Los errores de configuración y de base de datos se propagan
    al servicio que solicita la evaluación.
    """

    minimo_aciertos = obtener_minimo_aciertos()

    with obtener_conexion() as conexion:
        with conexion.cursor(row_factory=dict_row) as cursor:
            cantidad_aciertos = contar_aciertos_letra(
                cursor=cursor,
                id_usuario=id_usuario,
                id_letra=id_letra,
            )

            if cantidad_aciertos < minimo_aciertos:
                return None

            return registrar_aprendizaje(
                cursor=cursor,
                id_usuario=id_usuario,
                id_letra=id_letra,
            )