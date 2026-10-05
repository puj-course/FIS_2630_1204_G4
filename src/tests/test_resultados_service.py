import unittest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

from app.services.resultados_service import (
    LetraNoEncontradaError,
    registrar_resultado,
)
from src.schemas.resultados import ResultadoRegistrado


class TestRegistroResultadosPorSesion(unittest.TestCase):
    @patch("app.services.resultados_service.evaluar_aprendizaje")
    @patch("app.services.resultados_service.registrar_intento")
    @patch("app.services.resultados_service.obtener_conexion")
    def test_registra_aciertos_y_errores(
        self,
        obtener_conexion,
        registrar_intento,
        evaluar_aprendizaje,
    ):
        for detectada, ids_existentes, correcto in (
            (1, [1], True),
            (2, [1, 2], False),
        ):
            with self.subTest(detectada=detectada):
                registrar_intento.reset_mock()
                evaluar_aprendizaje.reset_mock()

                conexion = MagicMock()
                cursor = MagicMock()

                obtener_conexion.return_value.__enter__.return_value = (
                    conexion
                )
                conexion.cursor.return_value.__enter__.return_value = (
                    cursor
                )

                almacenado = {
                    "id_resultado": 20,
                    "id_sesion": 10,
                    "id_letra_objetivo": 1,
                    "id_letra_detectada": detectada,
                    "confianza": Decimal("0.9500"),
                    "es_correcto": correcto,
                    "fecha_resultado": datetime.now(timezone.utc),
                }

                cursor.fetchone.side_effect = [
                    {
                        "id_usuario": 9,
                        "estado": "activa",
                    },
                    almacenado,
                ]
                cursor.fetchall.return_value = [
                    {"id_letra": identificador}
                    for identificador in ids_existentes
                ]

                resultado = registrar_resultado(
                    id_usuario=9,
                    id_sesion=10,
                    id_letra_objetivo=1,
                    id_letra_detectada=detectada,
                    confianza=0.95,
                )

                self.assertEqual(resultado, almacenado)
                self.assertEqual(cursor.execute.call_count, 3)
                self.assertEqual(
                    cursor.execute.call_args.args[1],
                    (10, 1, detectada, 0.95, correcto),
                )

                registrar_intento.assert_called_once_with(
                    cursor=cursor,
                    id_resultado=almacenado["id_resultado"],
                    id_usuario=9,
                    id_sesion=10,
                    id_letra=1,
                    es_correcto=correcto,
                )

                if correcto:
                    evaluar_aprendizaje.assert_called_once_with(
                        id_usuario=9,
                        id_letra=1,
                    )
                else:
                    evaluar_aprendizaje.assert_not_called()

                salida = ResultadoRegistrado(**resultado)
                self.assertIs(salida.es_correcto, correcto)
                self.assertEqual(salida.id_sesion, 10)

    @patch("app.services.resultados_service.evaluar_aprendizaje")
    @patch("app.services.resultados_service.registrar_intento")
    @patch("app.services.resultados_service.obtener_conexion")
    def test_rechaza_letras_inexistentes(
        self,
        obtener_conexion,
        registrar_intento,
        evaluar_aprendizaje,
    ):
        for ids_existentes in ([], [1], [2]):
            with self.subTest(ids_existentes=ids_existentes):
                registrar_intento.reset_mock()
                evaluar_aprendizaje.reset_mock()

                conexion = MagicMock()
                cursor = MagicMock()

                obtener_conexion.return_value.__enter__.return_value = (
                    conexion
                )
                conexion.cursor.return_value.__enter__.return_value = (
                    cursor
                )

                cursor.fetchone.return_value = {
                    "id_usuario": 9,
                    "estado": "activa",
                }
                cursor.fetchall.return_value = [
                    {"id_letra": identificador}
                    for identificador in ids_existentes
                ]

                with self.assertRaises(LetraNoEncontradaError):
                    registrar_resultado(
                        id_usuario=9,
                        id_sesion=10,
                        id_letra_objetivo=1,
                        id_letra_detectada=2,
                        confianza=0.95,
                    )

                # Consulta sesión y letras sin insertar el resultado.
                self.assertEqual(cursor.execute.call_count, 2)
                registrar_intento.assert_not_called()
                evaluar_aprendizaje.assert_not_called()



class TestActualizacionProgresoDesdeResultados(unittest.TestCase):
    def setUp(self):
        def simular(nombre):
            parche = patch(f"app.services.resultados_service.{nombre}")
            simulado = parche.start()
            self.addCleanup(parche.stop)
            return simulado

        self.obtener_conexion = simular("obtener_conexion")
        self.registrar_intento = simular("registrar_intento")
        self.evaluar_aprendizaje = simular("evaluar_aprendizaje")
        self.contexto = self.obtener_conexion.return_value
        self.conexion = self.contexto.__enter__.return_value
        self.cursor = self.conexion.cursor.return_value.__enter__.return_value
        self.almacenado = {
            "id_resultado": 20,
            "id_sesion": 10,
            "id_letra_objetivo": 1,
            "id_letra_detectada": 1,
            "confianza": Decimal("0.9500"),
            "es_correcto": True,
            "fecha_resultado": datetime.now(timezone.utc),
        }
        self.cursor.fetchone.side_effect = [
            {"id_usuario": 9, "estado": "activa"},
            self.almacenado,
        ]
        self.cursor.fetchall.return_value = [{"id_letra": 1}]

    def registrar(self):
        return registrar_resultado(
            id_usuario=9,
            id_sesion=10,
            id_letra_objetivo=1,
            id_letra_detectada=1,
            confianza=0.95,
        )

    def test_actualiza_progreso_despues_de_confirmar_transaccion(self):
        eventos = []
        self.registrar_intento.side_effect = lambda **kwargs: eventos.append(
            "intento"
        )

        def confirmar(*args):
            self.assertEqual(args, (None, None, None))
            eventos.append("commit")
            return False

        def actualizar(**kwargs):
            self.assertEqual(eventos, ["intento", "commit"])
            eventos.append("progreso")

        self.contexto.__exit__.side_effect = confirmar
        self.evaluar_aprendizaje.side_effect = actualizar

        self.assertEqual(self.registrar(), self.almacenado)
        self.assertEqual(eventos, ["intento", "commit", "progreso"])
        self.evaluar_aprendizaje.assert_called_once_with(id_usuario=9, id_letra=1)

    def test_error_de_progreso_no_impide_devolver_resultado(self):
        self.evaluar_aprendizaje.side_effect = RuntimeError("Fallo de progreso")

        with self.assertLogs("app.services.resultados_service", level="ERROR"):
            resultado = self.registrar()

        self.assertEqual(resultado, self.almacenado)
        self.contexto.__exit__.assert_called_once_with(None, None, None)
        self.registrar_intento.assert_called_once()
        self.evaluar_aprendizaje.assert_called_once_with(id_usuario=9, id_letra=1)

    def test_error_de_commit_no_actualiza_progreso(self):
        self.contexto.__exit__.side_effect = RuntimeError("Fallo de commit")

        with self.assertRaisesRegex(RuntimeError, "Fallo de commit"):
            self.registrar()

        self.evaluar_aprendizaje.assert_not_called()

    def test_error_de_intento_no_actualiza_progreso(self):
        self.registrar_intento.side_effect = RuntimeError("Fallo de intento")

        with self.assertRaisesRegex(RuntimeError, "Fallo de intento"):
            self.registrar()

        self.evaluar_aprendizaje.assert_not_called()
        self.assertIs(self.contexto.__exit__.call_args.args[0], RuntimeError)

    def test_evaluacion_sin_nuevo_aprendizaje_devuelve_resultado(self):
        self.evaluar_aprendizaje.return_value = None

        resultado = self.registrar()

        self.assertEqual(resultado, self.almacenado)
        self.contexto.__exit__.assert_called_once_with(None, None, None)
        self.registrar_intento.assert_called_once()
        self.evaluar_aprendizaje.assert_called_once_with(
            id_usuario=9,
            id_letra=1,
        )


if __name__ == "__main__":
    unittest.main()
