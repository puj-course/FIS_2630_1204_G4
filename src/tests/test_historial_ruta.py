import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.security import crear_token_acceso


class TestHistorialRuta(unittest.TestCase):
    def setUp(self):
        anteriores = app.dependency_overrides.copy()
        app.dependency_overrides.clear()
        self.addCleanup(self.restaurar_overrides, anteriores)

        entorno = patch.dict(
            os.environ,
            {
                "JWT_SECRET": "clave-exclusiva-pruebas-historial-" * 2,
                "JWT_EXPIRE_MINUTES": "60",
            },
        )
        entorno.start()
        self.addCleanup(entorno.stop)

        self.consultar = self.iniciar_parche(
            "app.routes.historial.consultar_historial_usuario"
        )
        self.buscar_usuario = self.iniciar_parche(
            "app.security.obtener_usuario_por_id"
        )
        self.esta_revocado = self.iniciar_parche(
            "app.security.token_esta_revocado"
        )

        self.consultar.return_value = []
        self.buscar_usuario.return_value = {
            "id_usuario": 7,
            "rol": "usuario",
        }
        self.esta_revocado.return_value = False

        self.cliente = TestClient(app)
        self.addCleanup(self.cliente.close)

        self.cabeceras = self.crear_cabeceras(7)

    def iniciar_parche(self, destino):
        parche = patch(destino)
        simulacion = parche.start()
        self.addCleanup(parche.stop)
        return simulacion

    def restaurar_overrides(self, anteriores):
        app.dependency_overrides.clear()
        app.dependency_overrides.update(anteriores)

    def crear_cabeceras(self, id_usuario):
        token = crear_token_acceso(id_usuario)
        return {"Authorization": f"Bearer {token}"}

    def historial_ejemplo(self, id_usuario=7, id_sesion=10):
        return [
            {
                "id_sesion": id_sesion,
                "id_usuario": id_usuario,
                "fecha_inicio": "2026-10-09T09:00:00",
                "fecha_fin": None,
                "estado": "activa",
                "resultados": [
                    {
                        "id_resultado": 100,
                        "id_sesion": id_sesion,
                        "id_usuario": id_usuario,
                        "id_letra_objetivo": 1,
                        "letra_objetivo": "A",
                        "id_letra_detectada": 2,
                        "letra_detectada": "B",
                        "confianza": 0.85,
                        "es_correcto": False,
                        "fecha_resultado": "2026-10-09T09:01:00",
                    }
                ],
            }
        ]

    def comprobar_rechazo(self, cabeceras):
        respuesta = self.cliente.get(
            "/historial",
            headers=cabeceras,
        )

        self.assertEqual(respuesta.status_code, 401, respuesta.text)
        self.assertEqual(
            respuesta.json(),
            {"detail": "No fue posible validar las credenciales"},
        )
        self.assertEqual(
            respuesta.headers.get("www-authenticate"),
            "Bearer",
        )
        self.consultar.assert_not_called()

    def test_devuelve_actividades_del_usuario_autenticado(self):
        historial = self.historial_ejemplo()
        self.consultar.return_value = historial

        respuesta = self.cliente.get(
            "/historial",
            headers=self.cabeceras,
        )

        self.assertEqual(respuesta.status_code, 200, respuesta.text)
        self.assertEqual(
            respuesta.json(),
            {"total": 1, "historial": historial},
        )
        self.buscar_usuario.assert_called_once_with(7)
        self.consultar.assert_called_once_with(id_usuario=7)

    def test_usuario_sin_historial_recibe_respuesta_valida(self):
        respuesta = self.cliente.get(
            "/historial",
            headers=self.cabeceras,
        )

        self.assertEqual(respuesta.status_code, 200, respuesta.text)
        self.assertEqual(
            respuesta.json(),
            {"total": 0, "historial": []},
        )
        self.consultar.assert_called_once_with(id_usuario=7)

    def test_parametro_ajeno_no_cambia_el_usuario_del_token(self):
        usuarios = {
            7: {"id_usuario": 7, "rol": "usuario"},
            8: {"id_usuario": 8, "rol": "usuario"},
        }
        historiales = {
            7: self.historial_ejemplo(7, 10),
            8: self.historial_ejemplo(8, 20),
        }

        self.buscar_usuario.side_effect = usuarios.get
        self.consultar.side_effect = (
            lambda id_usuario: historiales[id_usuario]
        )

        for propietario, ajeno in ((7, 8), (8, 7)):
            with self.subTest(usuario=propietario):
                self.consultar.reset_mock()

                respuesta = self.cliente.get(
                    "/historial",
                    params={"id_usuario": ajeno},
                    headers=self.crear_cabeceras(propietario),
                )

                self.assertEqual(
                    respuesta.status_code,
                    200,
                    respuesta.text,
                )
                self.assertEqual(
                    respuesta.json(),
                    {
                        "total": 1,
                        "historial": historiales[propietario],
                    },
                )
                self.consultar.assert_called_once_with(
                    id_usuario=propietario,
                )

    def test_rechaza_credenciales_ausentes_o_invalidas(self):
        with patch.dict(
            os.environ,
            {"JWT_EXPIRE_MINUTES": "-1"},
        ):
            vencidas = self.crear_cabeceras(7)

        with patch.dict(
            os.environ,
            {"JWT_SECRET": "otra-clave-exclusiva-de-pruebas-" * 2},
        ):
            firma_incorrecta = self.crear_cabeceras(7)

        casos = {
            "sin_token": {},
            "token_malformado": {
                "Authorization": "Bearer token-invalido",
            },
            "token_vencido": vencidas,
            "firma_incorrecta": firma_incorrecta,
        }

        for nombre, cabeceras in casos.items():
            with self.subTest(caso=nombre):
                self.comprobar_rechazo(cabeceras)

        self.esta_revocado.assert_not_called()
        self.buscar_usuario.assert_not_called()

    def test_rechaza_token_revocado(self):
        self.esta_revocado.return_value = True

        self.comprobar_rechazo(self.cabeceras)

        self.esta_revocado.assert_called_once()
        self.buscar_usuario.assert_not_called()

    def test_rechaza_usuario_inexistente(self):
        self.buscar_usuario.return_value = None

        self.comprobar_rechazo(self.cabeceras)

        self.buscar_usuario.assert_called_once_with(7)

    def test_error_del_servicio_devuelve_mensaje_controlado(self):
        self.consultar.side_effect = RuntimeError(
            "Detalle interno que no debe aparecer en la respuesta"
        )

        with self.assertLogs("app.routes.historial", level="ERROR"):
            respuesta = self.cliente.get(
                "/historial",
                headers=self.cabeceras,
            )

        self.assertEqual(respuesta.status_code, 500, respuesta.text)
        self.assertEqual(
            respuesta.json(),
            {"detail": "No fue posible consultar el historial"},
        )
        self.consultar.assert_called_once_with(id_usuario=7)


if __name__ == "__main__":
    unittest.main()