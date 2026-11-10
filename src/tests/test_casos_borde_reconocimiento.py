import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.vision import letras_estaticas as letras
from app.vision import vocales
from app.vision.decoradores_reconocimiento import DecoradorMedicionTiempo
from app.vision.reconocimiento import (
    ReconocimientoEstatico,
    reconocer_mano,
)


class TestCasosBordeReconocimiento(unittest.TestCase):

    @patch(
        "app.vision.reconocimiento.reconocer_letra_movimiento",
        return_value=None,
    )
    def test_movimiento_sin_fotogramas(self, reconocer_movimiento):
        # Arrange
        mano = object()
        fotogramas = ()

        # Act
        resultado = reconocer_mano(
            mano=mano,
            fotogramas=fotogramas,
            modo="movimiento",
        )

        # Assert
        self.assertIsNone(resultado["letra"])
        self.assertTrue(resultado["requiere_movimiento"])

        reconocer_movimiento.assert_called_once_with(
            mano,
            fotogramas,
        )

    @patch(
        "app.vision.reconocimiento.reconocer_consonante_estatica",
        return_value="A",
    )
    def test_medicion_con_duracion_cero(self, reconocer_estatico):
        # Arrange
        decorador = DecoradorMedicionTiempo(
            ReconocimientoEstatico()
        )

        with patch(
            "app.vision.decoradores_reconocimiento.time.perf_counter",
            side_effect=[10.0, 10.0],
        ), patch(
            "app.vision.decoradores_reconocimiento._logger.info"
        ) as registrar:

            # Act
            resultado = decorador.reconocer(object())

        # Assert
        self.assertEqual(resultado["letra"], "A")
        reconocer_estatico.assert_called_once()
        registrar.assert_called_once()

        argumentos = registrar.call_args.args

        self.assertEqual(
            argumentos[1],
            "ReconocimientoEstatico",
        )
        self.assertEqual(argumentos[2], 0.0)
        self.assertEqual(argumentos[3], "reconocida")

class TestConsonantesEstaticas(unittest.TestCase):

    def crear_mano(self):
        return [
            SimpleNamespace(x=0.0, y=0.0, z=0.0)
            for _ in range(21)
        ]

    def comprobar_reconocimiento(
        self,
        dedos,
        esperado,
        *,
        distancias=None,
        pulgar=False,
        abajo=False,
        cruzados=False,
        gancho=False,
        curvos=False,
    ):
        mano = self.crear_mano()
        mano[4].y = 1.0
        distancias = distancias or {}

        with (
            patch.object(
                letras,
                "dedos_extendidos",
                return_value=dedos,
            ),
            patch.object(
                letras,
                "distancia_relativa",
                side_effect=lambda _mano, i, j: distancias.get(
                    (i, j), 10.0
                ),
            ),
            patch.object(
                letras,
                "pulgar_abierto",
                return_value=pulgar,
            ),
            patch.object(
                letras,
                "dedos_hacia_abajo",
                return_value=abajo,
            ),
            patch.object(
                letras,
                "indices_cruzados",
                return_value=cruzados,
            ),
            patch.object(
                letras,
                "indice_en_gancho",
                return_value=gancho,
            ),
            patch.object(
                letras,
                "dedos_curvos",
                return_value=curvos,
            ),
            patch.object(
                letras,
                "tamano_mano",
                return_value=1.0,
            ),
        ):
            self.assertEqual(
                letras.reconocer_consonante_estatica(mano),
                esperado,
            )

    def test_reconoce_consonantes_por_grupos(self):
        escenarios = [
            (
                "M",
                (True, True, True, False),
                {"abajo": True},
            ),
            (
                "W",
                (True, True, True, False),
                {
                    "distancias": {
                        (8, 12): 0.7,
                        (12, 16): 0.7,
                    }
                },
            ),
            (
                "N",
                (True, True, False, False),
                {"abajo": True},
            ),
            (
                "K",
                (True, True, False, False),
                {
                    "pulgar": True,
                    "distancias": {(8, 12): 0.7},
                },
            ),
            (
                "R",
                (True, True, False, False),
                {
                    "cruzados": True,
                    "distancias": {(8, 12): 0.45},
                },
            ),
            (
                "T",
                (True, True, False, False),
                {
                    "distancias": {
                        (8, 12): 0.3,
                        (4, 6): 0.6,
                    }
                },
            ),
            (
                "V",
                (True, True, False, False),
                {"distancias": {(8, 12): 0.7}},
            ),
            (
                "P",
                (True, False, False, False),
                {
                    "abajo": True,
                    "distancias": {(4, 8): 0.9},
                },
            ),
            (
                "D",
                (True, False, False, False),
                {"distancias": {(4, 12): 0.2}},
            ),
            (
                "L",
                (True, False, False, False),
                {
                    "pulgar": True,
                    "distancias": {(4, 8): 1.2},
                },
            ),
            (
                "Q",
                (False, False, False, False),
                {
                    "distancias": {
                        (4, 8): 0.2,
                        (4, 12): 0.2,
                        (4, 16): 0.2,
                        (4, 20): 0.2,
                    }
                },
            ),
            (
                "X",
                (False, False, False, False),
                {
                    "gancho": True,
                    "distancias": {(8, 5): 0.9},
                },
            ),
            (
                "B",
                (True, True, True, True),
                {
                    "distancias": {
                        (8, 12): 0.3,
                        (12, 16): 0.3,
                        (16, 20): 0.3,
                    }
                },
            ),
            (
                "C",
                (True, True, True, True),
                {
                    "curvos": True,
                    "distancias": {(4, 8): 0.8},
                },
            ),
            (
                "F",
                (True, False, False, True),
                {"pulgar": True},
            ),
            (
                "Y",
                (False, False, False, True),
                {
                    "pulgar": True,
                    "distancias": {(4, 20): 1.4},
                },
            ),
        ]

        for esperado, dedos, mediciones in escenarios:
            with self.subTest(letra=esperado):
                self.comprobar_reconocimiento(
                    dedos,
                    esperado,
                    **mediciones,
                )

    def test_no_reconoce_patron_sin_coincidencia(self):
        casos = [
            (
                (True, True, True, False),
                {"distancias": {(8, 12): 0.2}},
            ),
            (
                (True, True, False, False),
                {"distancias": {(8, 12): 0.45}},
            ),
            (
                (True, False, False, False),
                {},
            ),
            (
                (False, False, False, False),
                {},
            ),
            (
                (True, True, True, True),
                {},
            ),
            (
                (True, True, True, True),
                {"pulgar": True},
            ),
            (
                (True, False, False, True),
                {},
            ),
            (
                (False, False, False, True),
                {
                    "pulgar": True,
                    "distancias": {(4, 20): 1.0},
                },
            ),
        ]

        for dedos, mediciones in casos:
            with self.subTest(dedos=dedos):
                self.comprobar_reconocimiento(
                    dedos,
                    None,
                    **mediciones,
                )

    def test_rechaza_mano_incompleta(self):
        mano = self.crear_mano()[:20]

        resultado = letras.reconocer_consonante_estatica(mano)

        self.assertIsNone(resultado)

    def test_rechaza_patron_no_implementado(self):
        self.comprobar_reconocimiento(
            (False, True, True, True),
            None,
        )

    def test_dedos_extendidos(self):
        estados = {
            "indice": True,
            "medio": True,
            "anular": False,
            "menique": False,
        }

        with patch.object(
            letras,
            "dedo_estirado",
            side_effect=lambda _mano, dedo: estados[dedo],
        ):
            resultado = letras.dedos_extendidos(
                self.crear_mano()
            )

        self.assertEqual(
            resultado,
            (True, True, False, False),
        )

    def test_dedos_hacia_abajo(self):
        mano = self.crear_mano()

        mano[8].y = 0.8
        mano[12].y = 0.8

        with patch.object(
            letras,
            "tamano_mano",
            return_value=1.0,
        ):
            self.assertTrue(
                letras.dedos_hacia_abajo(mano, 0, 1)
            )

            mano[12].y = 0.2

            self.assertFalse(
                letras.dedos_hacia_abajo(mano, 0, 1)
            )

    def test_pulgar_abierto(self):
        casos = [
            (150, 0.7, 0.9, True),
            (130, 0.7, 0.9, False),
            (150, 0.3, 0.9, False),
            (150, 0.7, 0.5, False),
        ]

        for ang, d45, d49, esperado in casos:
            with self.subTest(angulo=ang):
                distancias = {
                    (4, 5): d45,
                    (4, 9): d49,
                }

                with (
                    patch.object(
                        letras,
                        "angulo",
                        return_value=ang,
                    ),
                    patch.object(
                        letras,
                        "distancia_relativa",
                        side_effect=lambda _mano, a, b: distancias[
                            (a, b)
                        ],
                    ),
                ):
                    resultado = letras.pulgar_abierto(
                        self.crear_mano()
                    )

                self.assertIs(resultado, esperado)

    def test_dedos_curvos(self):
        casos = [
            (110, True),
            (165, False),
            (60, False),
        ]

        for ang, esperado in casos:
            with self.subTest(angulo=ang):
                with patch.object(
                    letras,
                    "angulo",
                    return_value=ang,
                ):
                    resultado = letras.dedos_curvos(
                        self.crear_mano()
                    )

                self.assertIs(resultado, esperado)

    def test_indices_cruzados(self):
        mano = self.crear_mano()

        mano[5].x, mano[5].y = 0, 0
        mano[8].x, mano[8].y = 1, 1
        mano[9].x, mano[9].y = 0, 1
        mano[12].x, mano[12].y = 1, 0

        self.assertTrue(
            letras.indices_cruzados(mano)
        )

        mano[9].y = 2
        mano[12].y = 2

        self.assertFalse(
            letras.indices_cruzados(mano)
        )

    def test_indice_en_gancho(self):
        mano = self.crear_mano()

        casos = [
            (145, 100, True),
            (90, 100, False),
            (145, 155, False),
            (145, 50, False),
        ]

        for primer_angulo, segundo_angulo, esperado in casos:
            with self.subTest(
                primero=primer_angulo,
                segundo=segundo_angulo,
            ):
                with patch.object(
                    letras,
                    "angulo",
                    side_effect=lambda a, b, c: (
                        primer_angulo
                        if a is mano[5]
                        else segundo_angulo
                    ),
                ):
                    resultado = letras.indice_en_gancho(mano)

                self.assertIs(resultado, esperado)

class TestCoberturaVocales(unittest.TestCase):

    @staticmethod
    def crear_mano():
        return [
            SimpleNamespace(x=0.0, y=0.0, z=0.0)
            for _ in range(21)
        ]

    def test_distancia_3d(self):
        p = SimpleNamespace(x=0, y=0, z=0)
        q = SimpleNamespace(x=3, y=4, z=12)

        self.assertEqual(vocales.distancia(p, q), 13)
        self.assertEqual(vocales.distancia(p, p), 0)

    def test_angulo_recto_llano_y_vector_nulo(self):
        origen = SimpleNamespace(x=0, y=0, z=0)
        derecha = SimpleNamespace(x=1, y=0, z=0)
        arriba = SimpleNamespace(x=0, y=1, z=0)
        izquierda = SimpleNamespace(x=-1, y=0, z=0)

        self.assertAlmostEqual(
            vocales.angulo(derecha, origen, arriba),
            90,
        )

        self.assertAlmostEqual(
            vocales.angulo(derecha, origen, izquierda),
            180,
        )

        self.assertEqual(
            vocales.angulo(origen, origen, arriba),
            0,
        )

        self.assertEqual(
            vocales.angulo(derecha, origen, origen),
            0,
        )

    def test_tamano_y_distancias_relativas(self):
        mano = self.crear_mano()

        self.assertEqual(
            vocales.tamano_mano(mano),
            0.000001,
        )

        mano[9].y = 2.0
        mano[1].y = 0.0
        mano[2].y = 1.0

        self.assertEqual(
            vocales.tamano_mano(mano),
            2.0,
        )

        self.assertAlmostEqual(
            vocales.distancia_relativa(mano, 1, 2),
            0.5,
        )

    def test_dedo_estirado_con_angulos_limite(self):
        mano = self.crear_mano()

        casos = [
            ((160, 160), True),
            ((145, 160), False),
            ((160, 145), False),
        ]

        for angulos, esperado in casos:
            with self.subTest(angulos=angulos):
                with patch.object(
                    vocales,
                    "angulo",
                    side_effect=angulos,
                ):
                    resultado = vocales.dedo_estirado(
                        mano,
                        "indice",
                    )

                self.assertIs(resultado, esperado)

    def test_dedo_doblado_invierte_estado(self):
        mano = self.crear_mano()

        for estirado in (True, False):
            with patch.object(
                vocales,
                "dedo_estirado",
                return_value=estirado,
            ):
                resultado = vocales.dedo_doblado(
                    mano,
                    "medio",
                )

            self.assertIs(resultado, not estirado)

    def test_pulgar_estirado_angulo_y_direccion(self):
        mano = self.crear_mano()

        casos = [
            (160, -1, True),
            (140, -1, False),
            (160, 1, False),
        ]

        for ang, punta_y, esperado in casos:
            with self.subTest(angulo=ang, punta_y=punta_y):
                mano[3].y = 0
                mano[4].y = punta_y

                with patch.object(
                    vocales,
                    "angulo",
                    return_value=ang,
                ):
                    resultado = vocales.pulgar_estirado(mano)

                self.assertIs(resultado, esperado)

    def test_funciones_de_dedos_largos(self):
        mano = self.crear_mano()

        funciones = [
            (vocales.indice_estirado, "indice"),
            (vocales.medio_estirado, "medio"),
            (vocales.anular_estirado, "anular"),
            (vocales.menique_estirado, "menique"),
        ]

        for funcion, nombre in funciones:
            with self.subTest(dedo=nombre):
                with patch.object(
                    vocales,
                    "dedo_estirado",
                    return_value=True,
                ) as evaluar:
                    self.assertTrue(funcion(mano))
                    evaluar.assert_called_once_with(
                        mano,
                        nombre,
                    )

    def test_dedos_juntos_compara_puntas_y_limite(self):
        mano = self.crear_mano()

        with patch.object(
            vocales,
            "distancia_relativa",
            return_value=0.3,
        ) as distancia:
            self.assertTrue(
                vocales.dedos_juntos(
                    mano,
                    "indice",
                    "medio",
                )
            )

            distancia.assert_called_once_with(
                mano,
                8,
                12,
            )

        with patch.object(
            vocales,
            "distancia_relativa",
            return_value=0.5,
        ):
            self.assertFalse(
                vocales.dedos_juntos(
                    mano,
                    "indice",
                    "medio",
                )
            )

            self.assertTrue(
                vocales.dedos_juntos(
                    mano,
                    "indice",
                    "medio",
                    limite=0.6,
                )
            )

    def test_forma_circular_o_geometria(self):
        mano = self.crear_mano()

        # Establece una escala 2D de referencia de 1.
        mano[0].x = -1.0

        # Coloca las puntas próximas entre sí.
        mano[4].y = 1.0
        mano[8].y = 1.0
        mano[12].y = 1.1
        mano[16].y = 1.2
        mano[20].y = 1.3

        self.assertTrue(
            vocales.forma_circular_o(mano)
        )

        # Separa el pulgar del índice.
        mano[4].y = 2.0

        self.assertFalse(
            vocales.forma_circular_o(mano)
        )

        # Comprueba la protección frente a escala cero.
        mano[4].y = 1.0
        mano[0].x = 0.0

        self.assertFalse(
            vocales.forma_circular_o(mano)
        )

    def test_patrones_de_las_cinco_vocales(self):
        mano = self.crear_mano()

        pruebas = [
            (
                "A",
                vocales.es_vocal_a,
                True, True, False, False, False, True,
            ),
            (
                "A no",
                vocales.es_vocal_a,
                True, False, False, False, False, False,
            ),
            (
                "E",
                vocales.es_vocal_e,
                True, False, False, False, False, True,
            ),
            (
                "E no",
                vocales.es_vocal_e,
                True, False, True, False, False, False,
            ),
            (
                "I",
                vocales.es_vocal_i,
                True, False, False, False, True, True,
            ),
            (
                "I no",
                vocales.es_vocal_i,
                True, False, False, False, False, False,
            ),
            (
                "O",
                vocales.es_vocal_o,
                True, False, True, False, False, True,
            ),
            (
                "O no",
                vocales.es_vocal_o,
                True, False, False, False, False, False,
            ),
            (
                "U",
                vocales.es_vocal_u,
                True, False, False, True, True, True,
            ),
            (
                "U no",
                vocales.es_vocal_u,
                True, False, False, False, True, False,
            ),
        ]

        for (
            nombre,
            funcion,
            doblados,
            pulgar,
            circular,
            indice,
            menique,
            esperado,
        ) in pruebas:
            with self.subTest(nombre=nombre):
                with (
                    patch.object(
                        vocales,
                        "dedo_doblado",
                        return_value=doblados,
                    ),
                    patch.object(
                        vocales,
                        "pulgar_estirado",
                        return_value=pulgar,
                    ),
                    patch.object(
                        vocales,
                        "forma_circular_o",
                        return_value=circular,
                    ),
                    patch.object(
                        vocales,
                        "indice_estirado",
                        return_value=indice,
                    ),
                    patch.object(
                        vocales,
                        "menique_estirado",
                        return_value=menique,
                    ),
                ):
                    self.assertIs(
                        funcion(mano),
                        esperado,
                    )

    def test_reconocer_vocal_en_orden_y_sin_coincidencia(self):
        mano = self.crear_mano()

        for esperado in ("O", "U", "I", "A", "E", None):
            with self.subTest(esperado=esperado):
                estados = {
                    "O": esperado == "O",
                    "U": esperado == "U",
                    "I": esperado == "I",
                    "A": esperado == "A",
                    "E": esperado == "E",
                }

                with (
                    patch.object(
                        vocales,
                        "es_vocal_o",
                        return_value=estados["O"],
                    ),
                    patch.object(
                        vocales,
                        "es_vocal_u",
                        return_value=estados["U"],
                    ),
                    patch.object(
                        vocales,
                        "es_vocal_i",
                        return_value=estados["I"],
                    ),
                    patch.object(
                        vocales,
                        "es_vocal_a",
                        return_value=estados["A"],
                    ),
                    patch.object(
                        vocales,
                        "es_vocal_e",
                        return_value=estados["E"],
                    ),
                ):
                    self.assertEqual(
                        vocales.reconocer_vocal(mano),
                        esperado,
                    )

        # Comprueba que O tiene prioridad sobre U.
        with (
            patch.object(
                vocales,
                "es_vocal_o",
                return_value=True,
            ),
            patch.object(
                vocales,
                "es_vocal_u",
                return_value=True,
            ),
        ):
            self.assertEqual(
                vocales.reconocer_vocal(mano),
                "O",
            )

if __name__ == "__main__":
    unittest.main()
