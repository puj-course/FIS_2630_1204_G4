from psycopg.rows import dict_row

from conf.database import obtener_conexion


class LetraObjetivoNoEncontradaError(Exception):
    pass


class LetraDetectadaNoEncontradaError(Exception):
    pass


def registrar_resultado_reconocimiento(
    id_usuario: int,
    id_letra_objetivo: int,
    letra_detectada: str,
    confianza: float,
):
    """
    Crea una sesión y registra el resultado del reconocimiento.
    """

    with obtener_conexion() as conexion:
        with conexion.cursor(row_factory=dict_row) as cursor:

            # Busca la letra que el usuario está practicando
            cursor.execute(
                """
                SELECT
                    id_letra,
                    letra
                FROM letras
                WHERE id_letra = %s
                    AND activa = TRUE;
                """,
                (id_letra_objetivo,)
            )

            letra_objetivo = cursor.fetchone()

            if letra_objetivo is None:
                raise LetraObjetivoNoEncontradaError(
                    "La letra objetivo no existe o no está activa"
                )

            # Busca la letra encontrada por el reconocimiento
            cursor.execute(
                """
                SELECT
                    id_letra,
                    letra
                FROM letras
                WHERE UPPER(letra) = %s
                    AND activa = TRUE;
                """,
                (letra_detectada,)
            )

            letra_detectada_registrada = cursor.fetchone()

            if letra_detectada_registrada is None:
                raise LetraDetectadaNoEncontradaError(
                    "La letra detectada no existe o no está activa"
                )

            # Crea una sesión asociada al usuario autenticado
            cursor.execute(
                """
                INSERT INTO sesiones_reconocimiento (
                    id_usuario,
                    fecha_fin,
                    estado
                )
                VALUES (
                    %s,
                    CURRENT_TIMESTAMP,
                    'finalizada'
                )
                RETURNING id_sesion;
                """,
                (id_usuario,)
            )

            sesion = cursor.fetchone()

            id_letra_detectada = (
                letra_detectada_registrada["id_letra"]
            )

            es_correcto = (
                id_letra_objetivo == id_letra_detectada
            )

            # Guarda el resultado dentro de la sesión
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
                    confianza,
                    es_correcto,
                    fecha_resultado;
                """,
                (
                    sesion["id_sesion"],
                    id_letra_objetivo,
                    id_letra_detectada,
                    confianza,
                    es_correcto
                )
            )

            resultado = cursor.fetchone()

    return {
        "id_resultado": resultado["id_resultado"],
        "id_sesion": sesion["id_sesion"],
        "id_usuario": id_usuario,
        "id_letra_objetivo": letra_objetivo["id_letra"],
        "letra_objetivo": letra_objetivo["letra"],
        "id_letra_detectada": id_letra_detectada,
        "letra_detectada": letra_detectada_registrada["letra"],
        "confianza": float(resultado["confianza"]),
        "es_correcto": resultado["es_correcto"],
        "fecha_resultado": resultado["fecha_resultado"]
    }