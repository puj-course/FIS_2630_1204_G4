
import unittest
from unittest.mock import patch

from psycopg.rows import dict_row

from app.services.letras_service import (
    actualizar_informacion_letra,
    obtener_letra_por_id,
    obtener_letras_registradas,
)


class TestLetrasService(unittest.TestCase):

    def setUp(self):
        parche = patch(
            "app.services.letras_service.obtener_conexion"
        )
        self.obtener_conexion = parche.start()
        self.addCleanup(parche.stop)

        self.conexion = (
            self.obtener_conexion.return_value
            .__enter__.return_value
        )
        self.cursor = (
            self.conexion.cursor.return_value
            .__enter__.return_value
        )

        self.letra = {
            "id_letra": 1,
            "letra": "A",
            "descripcion": "Letra A",
            "ruta_imagen": "assets/alfabeto/a.png",
        }

    def test_consulta_letras_activas(self):
        # Arrange
        self.cursor.fetchall.return_value = [self.letra]

        # Act
        resultado = obtener_letras_registradas()

        # Assert
        self.assertEqual(resultado, [self.letra])
        self.conexion.cursor.assert_called_once_with(
            row_factory=dict_row
        )

        consulta = self.cursor.execute.call_args.args[0]
        self.assertIn("WHERE activa = TRUE", consulta)
        self.assertIn("ORDER BY letra", consulta)

    def test_consulta_sin_letras(self):
        # Arrange
        self.cursor.fetchall.return_value = []

        # Act
        resultado = obtener_letras_registradas()

        # Assert
        self.assertEqual(resultado, [])

    def test_consulta_letra_por_id(self):
        # Arrange
        self.cursor.fetchone.return_value = self.letra

        # Act
        resultado = obtener_letra_por_id(1)

        # Assert
        self.assertEqual(resultado, self.letra)
        parametros = self.cursor.execute.call_args.args[1]
        self.assertEqual(parametros, (1,))

    def test_consulta_letra_inexistente(self):
        # Arrange
        self.cursor.fetchone.return_value = None

        # Act
        resultado = obtener_letra_por_id(999)

        # Assert
        self.assertIsNone(resultado)

    def test_actualiza_solo_descripcion(self):
        # Arrange
        actualizada = {
            **self.letra,
            "descripcion": "Nueva descripcion",
        }
        self.cursor.fetchone.return_value = actualizada

        # Act
        resultado = actualizar_informacion_letra(
            1,
            {"descripcion": "Nueva descripcion"},
        )

        # Assert
        self.assertEqual(resultado, actualizada)

        parametros = self.cursor.execute.call_args.args[1]
        self.assertEqual(
            parametros,
            (True, "Nueva descripcion", False, None, 1),
        )

    def test_actualiza_solo_ruta_imagen(self):
        # Arrange
        actualizada = {
            **self.letra,
            "ruta_imagen": "assets/alfabeto/nueva_a.png",
        }
        self.cursor.fetchone.return_value = actualizada

        # Act
        resultado = actualizar_informacion_letra(
            1,
            {"ruta_imagen": "assets/alfabeto/nueva_a.png"},
        )

        # Assert
        self.assertEqual(resultado, actualizada)

        parametros = self.cursor.execute.call_args.args[1]
        self.assertEqual(
            parametros,
            (
                False,
                None,
                True,
                "assets/alfabeto/nueva_a.png",
                1,
            ),
        )

    def test_actualiza_ambos_campos(self):
        # Arrange
        cambios = {
            "descripcion": "Descripcion modificada",
            "ruta_imagen": "assets/alfabeto/nueva.png",
        }
        self.cursor.fetchone.return_value = {
            **self.letra,
            **cambios,
        }

        # Act
        resultado = actualizar_informacion_letra(
            1,
            cambios,
        )

        # Assert
        self.assertEqual(
            resultado["descripcion"],
            "Descripcion modificada",
        )
        self.assertEqual(
            resultado["ruta_imagen"],
            "assets/alfabeto/nueva.png",
        )

        parametros = self.cursor.execute.call_args.args[1]
        self.assertEqual(
            parametros,
            (
                True,
                "Descripcion modificada",
                True,
                "assets/alfabeto/nueva.png",
                1,
            ),
        )

    def test_actualiza_letra_inexistente(self):
        # Arrange
        self.cursor.fetchone.return_value = None

        # Act
        resultado = actualizar_informacion_letra(
            999,
            {"descripcion": "Nueva descripcion"},
        )

        # Assert
        self.assertIsNone(resultado)
        parametros = self.cursor.execute.call_args.args[1]
        self.assertEqual(parametros[-1], 999)


if __name__ == "__main__":
    unittest.main()
