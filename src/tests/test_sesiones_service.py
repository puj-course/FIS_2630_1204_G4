import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from app.services.sesiones_service import (
    EstadoSesionError,
    SesionNoEncontradaError,
    UsuarioNoEncontradoError,
    consultar_sesion,
    crear_sesion,
    finalizar_sesion,
)


class TestSesionesService(unittest.TestCase):
    def setUp(self):
        parche = patch(
            "app.services.sesiones_service.obtener_conexion"
        )
        self.obtener_conexion = parche.start()
        self.addCleanup(parche.stop)

        self.conexion = MagicMock()
        self.cursor = MagicMock()

        self.obtener_conexion.return_value.__enter__.return_value = (
            self.conexion
        )
        self.conexion.cursor.return_value.__enter__.return_value = (
            self.cursor
        )

        self.fecha_inicio = datetime.now(timezone.utc)

        self.sesion = {
            "id_sesion": 10,
            "id_usuario": 9,
            "fecha_inicio": self.fecha_inicio,
            "fecha_fin": None,
            "estado": "activa",
        }

    def test_crea_sesion_para_usuario_existente(self):
        self.cursor.fetchone.side_effect = [
            {"id_usuario": 9},
            self.sesion,
        ]

        resultado = crear_sesion(id_usuario=9)

        self.assertEqual(resultado, self.sesion)
        self.assertEqual(resultado["id_usuario"], 9)
        self.assertEqual(resultado["estado"], "activa")
        self.assertIsNone(resultado["fecha_fin"])

        self.assertEqual(self.cursor.execute.call_count, 2)
        self.assertEqual(
            self.cursor.execute.call_args_list[0].args[1],
            (9,),
        )
        self.assertEqual(
            self.cursor.execute.call_args_list[1].args[1],
            (9,),
        )

    def test_rechaza_usuario_inexistente_sin_insertar(self):
        self.cursor.fetchone.return_value = None

        with self.assertRaises(UsuarioNoEncontradoError):
            crear_sesion(id_usuario=999)

        self.assertEqual(self.cursor.execute.call_count, 1)

    def test_consulta_sesion_filtrando_por_propietario(self):
        self.cursor.fetchone.return_value = self.sesion

        resultado = consultar_sesion(
            id_usuario=9,
            id_sesion=10,
        )

        self.assertEqual(resultado, self.sesion)

        consulta, parametros = self.cursor.execute.call_args.args
        consulta = " ".join(consulta.split())

        self.assertIn("WHERE id_sesion = %s", consulta)
        self.assertIn("AND id_usuario = %s", consulta)
        self.assertEqual(parametros, (10, 9))

    def test_consulta_rechaza_sesion_no_disponible_para_usuario(self):
        self.cursor.fetchone.return_value = None

        with self.assertRaises(SesionNoEncontradaError):
            consultar_sesion(
                id_usuario=15,
                id_sesion=10,
            )

        self.assertEqual(
            self.cursor.execute.call_args.args[1],
            (10, 15),
        )

    def test_finaliza_sesion_activa(self):
        finalizada = {
            **self.sesion,
            "estado": "finalizada",
            "fecha_fin": self.fecha_inicio + timedelta(minutes=5),
        }

        self.cursor.fetchone.side_effect = [
            self.sesion,
            finalizada,
        ]

        resultado = finalizar_sesion(
            id_usuario=9,
            id_sesion=10,
        )

        self.assertEqual(resultado, finalizada)
        self.assertEqual(self.cursor.execute.call_count, 2)

        consulta, parametros = (
            self.cursor.execute.call_args_list[0].args
        )
        consulta = " ".join(consulta.split())

        self.assertIn("AND id_usuario = %s", consulta)
        self.assertIn("FOR UPDATE", consulta)
        self.assertEqual(parametros, (10, 9))

        actualizacion, parametros = (
            self.cursor.execute.call_args_list[1].args
        )
        actualizacion = " ".join(actualizacion.split())

        self.assertIn("estado = 'finalizada'", actualizacion)
        self.assertIn("fecha_fin =", actualizacion)
        self.assertIn("CURRENT_TIMESTAMP", actualizacion)
        self.assertIn("WHERE id_sesion = %s", actualizacion)
        self.assertIn("AND id_usuario = %s", actualizacion)
        self.assertIn("AND estado = 'activa'", actualizacion)
        self.assertEqual(parametros, (10, 9))

    def test_finalizar_nuevamente_conserva_fecha_original(self):
        finalizada = {
            **self.sesion,
            "estado": "finalizada",
            "fecha_fin": self.fecha_inicio + timedelta(minutes=5),
        }
        self.cursor.fetchone.return_value = finalizada

        resultado = finalizar_sesion(
            id_usuario=9,
            id_sesion=10,
        )

        self.assertEqual(resultado, finalizada)
        self.assertEqual(
            resultado["fecha_fin"],
            finalizada["fecha_fin"],
        )
        # No ejecuta una segunda actualización.
        self.assertEqual(self.cursor.execute.call_count, 1)

    def test_rechaza_finalizar_sesion_cancelada(self):
        self.cursor.fetchone.return_value = {
            **self.sesion,
            "estado": "cancelada",
        }

        with self.assertRaises(EstadoSesionError):
            finalizar_sesion(
                id_usuario=9,
                id_sesion=10,
            )

        self.assertEqual(self.cursor.execute.call_count, 1)

    def test_finalizacion_rechaza_sesion_no_disponible_para_usuario(self):
        self.cursor.fetchone.return_value = None

        with self.assertRaises(SesionNoEncontradaError):
            finalizar_sesion(
                id_usuario=15,
                id_sesion=10,
            )

        self.assertEqual(self.cursor.execute.call_count, 1)
        self.assertEqual(
            self.cursor.execute.call_args.args[1],
            (10, 15),
        )

    def test_propaga_error_de_almacenamiento(self):
        self.cursor.fetchone.return_value = {"id_usuario": 9}
        self.cursor.execute.side_effect = [
            None,
            RuntimeError("Fallo simulado de almacenamiento"),
        ]

        with self.assertRaisesRegex(
            RuntimeError,
            "Fallo simulado de almacenamiento",
        ):
            crear_sesion(id_usuario=9)

        # El error alcanza el contexto de conexión para que
        # psycopg pueda revertir la transacción.
        salida = self.obtener_conexion.return_value.__exit__
        self.assertIs(salida.call_args.args[0], RuntimeError)


if __name__ == "__main__":
    unittest.main()