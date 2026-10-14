import unittest
from copy import deepcopy
from datetime import datetime
from unittest.mock import patch

from app.services.historial_service import consultar_historial_usuario


class TestHistorialService(unittest.TestCase):
    def setUp(self):
        parche_sesiones = patch(
            "app.services.historial_service.consultar_sesiones_usuario"
        )
        parche_resultados = patch(
            "app.services.historial_service.obtener_resultados_usuario"
        )

        self.consultar_sesiones = parche_sesiones.start()
        self.addCleanup(parche_sesiones.stop)

        self.obtener_resultados = parche_resultados.start()
        self.addCleanup(parche_resultados.stop)

    def test_usuario_sin_sesiones_recibe_lista_vacia(self):
        self.consultar_sesiones.return_value = []

        historial = consultar_historial_usuario(7)

        self.assertEqual(historial, [])
        self.consultar_sesiones.assert_called_once_with(7)
        self.obtener_resultados.assert_not_called()

    def test_conserva_sesion_sin_resultados(self):
        sesion = {
            "id_sesion": 10,
            "id_usuario": 7,
            "fecha_inicio": datetime(2026, 10, 7, 9),
            "fecha_fin": None,
            "estado": "activa",
        }
        self.consultar_sesiones.return_value = [sesion]
        self.obtener_resultados.return_value = []

        historial = consultar_historial_usuario(7)

        self.assertEqual(historial, [{**sesion, "resultados": []}])
        self.consultar_sesiones.assert_called_once_with(7)
        self.obtener_resultados.assert_called_once_with(7)

    def test_agrupa_y_ordena_sin_modificar_los_datos_recibidos(self):
        fecha = datetime(2026, 10, 7, 9)
        fecha_posterior = datetime(2026, 10, 7, 10)

        sesiones = [
            {
                "id_sesion": 10,
                "id_usuario": 7,
                "fecha_inicio": fecha,
                "fecha_fin": fecha_posterior,
                "estado": "finalizada",
            },
            {
                "id_sesion": 20,
                "id_usuario": 7,
                "fecha_inicio": fecha_posterior,
                "fecha_fin": None,
                "estado": "activa",
            },
        ]

        def resultado(id_resultado, id_sesion, fecha_resultado, correcto):
            return {
                "id_resultado": id_resultado,
                "id_sesion": id_sesion,
                "id_usuario": 7,
                "id_letra_objetivo": 1,
                "letra_objetivo": "A",
                "id_letra_detectada": 1 if correcto else 2,
                "letra_detectada": "A" if correcto else "B",
                "confianza": 0.95,
                "es_correcto": correcto,
                "fecha_resultado": fecha_resultado,
            }

        resultados = [
            resultado(1, 10, fecha, True),
            resultado(4, 20, fecha_posterior, False),
            resultado(3, 10, fecha_posterior, False),
            resultado(2, 10, fecha_posterior, True),
        ]

        sesiones_originales = deepcopy(sesiones)
        resultados_originales = deepcopy(resultados)

        self.consultar_sesiones.return_value = sesiones
        self.obtener_resultados.return_value = resultados

        historial = consultar_historial_usuario(7)

        self.assertEqual(
            [sesion["id_sesion"] for sesion in historial],
            [20, 10],
        )
        self.assertEqual(historial[0]["resultados"], [resultados[1]])
        self.assertEqual(
            historial[1]["resultados"],
            [resultados[2], resultados[3], resultados[0]],
        )
        self.assertEqual(sesiones, sesiones_originales)
        self.assertEqual(resultados, resultados_originales)
        self.consultar_sesiones.assert_called_once_with(7)
        self.obtener_resultados.assert_called_once_with(7)


if __name__ == "__main__":
    unittest.main()