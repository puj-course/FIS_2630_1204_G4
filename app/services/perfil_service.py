from psycopg.rows import dict_row

from conf.database import obtener_conexion


def obtener_progreso_usuario(id_usuario: int):
    with obtener_conexion() as conexion:
        with conexion.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    COUNT(l.id_letra) AS total_letras,
                    COUNT(p.id_progreso) FILTER (
                        WHERE p.cantidad_intentos > 0
                    ) AS letras_iniciadas,
                    COUNT(p.id_progreso) FILTER (
                        WHERE p.dominada = TRUE
                    ) AS letras_dominadas,
                    COALESCE(
                        SUM(p.cantidad_intentos),
                        0
                    ) AS cantidad_intentos,
                    COALESCE(
                        SUM(p.cantidad_aciertos),
                        0
                    ) AS cantidad_aciertos
                FROM letras AS l
                LEFT JOIN progreso_usuario AS p
                    ON p.id_letra = l.id_letra
                    AND p.id_usuario = %s
                WHERE l.activa = TRUE;
                """,
                (id_usuario,)
            )

            progreso = cursor.fetchone()

    total_letras = progreso["total_letras"]
    letras_dominadas = progreso["letras_dominadas"]

    porcentaje = (
        round(
            letras_dominadas * 100 / total_letras,
            2
        )
        if total_letras > 0
        else 0.0
    )

    return {
        **progreso,
        "porcentaje_progreso": porcentaje
    }