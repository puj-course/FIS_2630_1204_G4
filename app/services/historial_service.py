from app.services.resultados_reconocimiento_service import (
    obtener_resultados_usuario,
)
from app.services.sesiones_service import consultar_sesiones_usuario


def consultar_historial_usuario(id_usuario: int):
    """Consulta las sesiones y sus resultados, de más recientes a antiguos.

    El identificador debe proceder del usuario autenticado.
    Incluye sesiones sin resultados y devuelve [] si no hay sesiones.
    No modifica los registros almacenados.
    """
    sesiones = consultar_sesiones_usuario(id_usuario)

    if not sesiones:
        return []

    resultados = obtener_resultados_usuario(id_usuario)

    resultados_por_sesion = {}

    for resultado in resultados:
        id_sesion = resultado["id_sesion"]
        resultados_por_sesion.setdefault(id_sesion, []).append(
            dict(resultado)
        )

    sesiones_ordenadas = sorted(
        sesiones,
        key=lambda sesion: (
            sesion["fecha_inicio"],
            sesion["id_sesion"],
        ),
        reverse=True,
    )

    historial = []

    for sesion in sesiones_ordenadas:
        resultados_sesion = sorted(
            resultados_por_sesion.get(sesion["id_sesion"], []),
            key=lambda resultado: (
                resultado["fecha_resultado"],
                resultado["id_resultado"],
            ),
            reverse=True,
        )

        historial.append(
            {
                **sesion,
                "resultados": resultados_sesion,
            }
        )

    return historial