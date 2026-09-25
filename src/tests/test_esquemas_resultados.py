import unittest
from datetime import datetime, timezone
from decimal import Decimal

from pydantic import ValidationError

from src.schemas.resultados import (
    RegistrarResultadoEntrada,
    ResultadoRegistrado,
    ResultadoRespuesta,
    ResultadosConsultaRespuesta,
)


class TestEsquemasResultados(unittest.TestCase):
    def setUp(self):
        self.entrada = {
            "id_sesion": 10,
            "id_letra_objetivo": 1,
            "id_letra_detectada": 1,
            "confianza": 0.95,
        }

        self.resultado = {
            "id_resultado": 20,
            "id_sesion": 10,
            "id_letra_objetivo": 1,
            "id_letra_detectada": 1,
            "confianza": Decimal("0.9500"),
            "es_correcto": True,
            "fecha_resultado": datetime.now(timezone.utc),
        }

    def test_acepta_entrada_valida(self):
        entrada = RegistrarResultadoEntrada(**self.entrada)

        self.assertEqual(entrada.model_dump(), self.entrada)

    def test_rechaza_campos_requeridos_ausentes(self):
        for campo in self.entrada:
            with self.subTest(campo=campo):
                datos = self.entrada.copy()
                del datos[campo]

                with self.assertRaises(ValidationError):
                    RegistrarResultadoEntrada(**datos)

    def test_rechaza_identificadores_invalidos(self):
        for campo in (
            "id_sesion",
            "id_letra_objetivo",
            "id_letra_detectada",
        ):
            for valor in (0, -1, "1", 1.5, True, None):
                with self.subTest(campo=campo, valor=valor):
                    datos = {**self.entrada, campo: valor}

                    with self.assertRaises(ValidationError):
                        RegistrarResultadoEntrada(**datos)

    def test_acepta_limites_de_confianza(self):
        for valor in (0, 1, 0.0, 1.0):
            with self.subTest(valor=valor):
                datos = {**self.entrada, "confianza": valor}
                entrada = RegistrarResultadoEntrada(**datos)

                self.assertEqual(entrada.confianza, valor)

    def test_rechaza_confianza_invalida(self):
        for valor in (
            -0.01,
            1.01,
            "0.95",
            True,
            None,
            float("nan"),
            float("inf"),
            float("-inf"),
        ):
            with self.subTest(valor=valor):
                datos = {**self.entrada, "confianza": valor}

                with self.assertRaises(ValidationError):
                    RegistrarResultadoEntrada(**datos)

    def test_rechaza_campos_adicionales(self):
        for campo, valor in (
            ("id_usuario", 999),
            ("es_correcto", True),
            ("fecha_resultado", "2026-09-25"),
        ):
            with self.subTest(campo=campo):
                datos = {**self.entrada, campo: valor}

                with self.assertRaises(ValidationError):
                    RegistrarResultadoEntrada(**datos)

    def test_serializa_resultado_con_tipos_de_postgresql(self):
        respuesta = ResultadoRespuesta(
            mensaje="Resultado registrado correctamente",
            resultado=ResultadoRegistrado(**self.resultado),
        )

        datos = respuesta.model_dump(mode="json")

        self.assertEqual(datos["resultado"]["confianza"], 0.95)
        self.assertIs(datos["resultado"]["es_correcto"], True)
        self.assertIsInstance(
            datos["resultado"]["fecha_resultado"],
            str,
        )

    def test_rechaza_salida_invalida(self):
        for campo, valor in (
            ("id_resultado", 0),
            ("id_sesion", -1),
            ("id_letra_objetivo", 0),
            ("id_letra_detectada", -1),
            ("confianza", 2),
            ("es_correcto", "true"),
            ("fecha_resultado", "fecha-invalida"),
        ):
            with self.subTest(campo=campo):
                datos = {**self.resultado, campo: valor}

                with self.assertRaises(ValidationError):
                    ResultadoRegistrado(**datos)

    def test_consulta_con_resultados(self):
        consulta = ResultadosConsultaRespuesta(
            total=1,
            resultados=[self.resultado],
        )

        self.assertEqual(len(consulta.resultados), 1)
        self.assertEqual(consulta.resultados[0].id_sesion, 10)

    def test_consulta_vacia(self):
        consulta = ResultadosConsultaRespuesta(
            total=0,
            resultados=[],
        )

        self.assertEqual(
            consulta.model_dump(),
            {"total": 0, "resultados": []},
        )


if __name__ == "__main__":
    unittest.main()