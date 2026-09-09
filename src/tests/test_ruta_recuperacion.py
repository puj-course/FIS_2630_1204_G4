import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from fastapi import APIRouter, BackgroundTasks, FastAPI, Response
from fastapi.testclient import TestClient

from app.routes.recuperacion_contrasena import (
    MENSAJE_RECUPERACION,
    procesar_solicitud_recuperacion,
    router,
    solicitar_recuperacion
)
from app.services.correo_recuperacion_service import (
    ConfiguracionCorreo,
    ConfiguracionCorreoError
)
from app.services.recuperacion_service import RecuperacionCreada
from src.schemas.recuperacion import SolicitudRecuperacion


class TestRutaRecuperacion(unittest.TestCase):
    def setUp(self):
        self.configuracion = ConfiguracionCorreo(
            host="smtp-mail.outlook.com",
            puerto=587,
            seguridad="starttls",
            usuario="cuenta@example.com",
            client_id="11111111-2222-4333-8444-555555555555",
            remitente="cuenta@example.com",
            url_recuperacion="https://signia.example.com/restablecer-contrasena"
        )
        self.solicitud = RecuperacionCreada(
            id_recuperacion=20,
            correo="persona@example.com",
            token="token-exclusivo-de-prueba",
            fecha_expiracion=datetime(2026, 1, 1, 12, 15, tzinfo=timezone.utc)
        )

        for atributo, funcion, resultado in (
            ("configurar", "obtener_configuracion_correo", self.configuracion),
            ("crear", "crear_solicitud_recuperacion", self.solicitud),
            ("enviar", "enviar_correo_recuperacion", None)
        ):
            parche = patch(
                f"app.routes.recuperacion_contrasena.{funcion}",
                return_value=resultado
            )
            setattr(self, atributo, parche.start())
            self.addCleanup(parche.stop)

        aplicacion = FastAPI()
        autenticacion = APIRouter(prefix="/auth")
        autenticacion.include_router(router)
        aplicacion.include_router(autenticacion)
        self.cliente = TestClient(aplicacion)
        self.addCleanup(self.cliente.close)

    def test_acepta_solicitud_sin_exigir_login(self):
        respuesta = self.cliente.post(
            "/auth/recuperar-contrasena",
            json={"correo": "persona@example.com"}
        )

        self.assertEqual(respuesta.status_code, 202)
        self.assertEqual(respuesta.json(), {"mensaje": MENSAJE_RECUPERACION})
        self.assertEqual(respuesta.headers["Cache-Control"], "no-store")
        self.crear.assert_called_once_with("persona@example.com")
        self.enviar.assert_called_once_with(
            correo=self.solicitud.correo,
            token=self.solicitud.token,
            fecha_expiracion=self.solicitud.fecha_expiracion,
            configuracion=self.configuracion
        )

    def test_usa_misma_respuesta_para_usuario_inexistente(self):
        registrada = self.cliente.post(
            "/auth/recuperar-contrasena",
            json={"correo": "persona@example.com"}
        )
        self.crear.return_value = None
        self.enviar.reset_mock()

        inexistente = self.cliente.post(
            "/auth/recuperar-contrasena",
            json={"correo": "nadie@example.com"}
        )

        self.assertEqual(inexistente.status_code, registrada.status_code)
        self.assertEqual(inexistente.json(), registrada.json())
        self.enviar.assert_not_called()

    def test_no_envia_correo_si_servicio_descarta_solicitud_repetida(self):
        self.crear.return_value = None

        respuesta = self.cliente.post(
            "/auth/recuperar-contrasena",
            json={"correo": "persona@example.com"}
        )

        self.assertEqual(respuesta.status_code, 202)
        self.enviar.assert_not_called()

    def test_normaliza_correo_antes_de_procesar(self):
        respuesta = self.cliente.post(
            "/auth/recuperar-contrasena",
            json={"correo": "  Persona@Example.COM  "}
        )

        self.assertEqual(respuesta.status_code, 202)
        self.crear.assert_called_once_with("persona@example.com")

    def test_rechaza_datos_invalidos_antes_de_procesar(self):
        for datos in ({}, {"correo": "invalido"}, {"correo": None}):
            with self.subTest(datos=datos):
                respuesta = self.cliente.post(
                    "/auth/recuperar-contrasena", json=datos
                )
                self.assertEqual(respuesta.status_code, 422)

        self.configurar.assert_not_called()
        self.crear.assert_not_called()
        self.enviar.assert_not_called()

    def test_rechaza_identificador_y_token_en_la_solicitud(self):
        for campo, valor in (("id_usuario", 5), ("token", "otro-token")):
            with self.subTest(campo=campo):
                respuesta = self.cliente.post(
                    "/auth/recuperar-contrasena",
                    json={"correo": "persona@example.com", campo: valor}
                )
                self.assertEqual(respuesta.status_code, 422)

        self.crear.assert_not_called()

    def test_no_expone_token_ni_credenciales_en_respuesta(self):
        respuesta = self.cliente.post(
            "/auth/recuperar-contrasena",
            json={"correo": "persona@example.com"}
        )

        self.assertNotIn(self.solicitud.token, respuesta.text)
        self.assertNotIn(self.configuracion.usuario, respuesta.text)
        self.assertEqual(set(respuesta.json()), {"mensaje"})

    def test_configuracion_incompleta_responde_503_sin_consultar_usuario(self):
        self.configurar.side_effect = ConfiguracionCorreoError("Error simulado")

        respuesta = self.cliente.post(
            "/auth/recuperar-contrasena",
            json={"correo": "persona@example.com"}
        )

        self.assertEqual(respuesta.status_code, 503)
        self.assertNotIn("Error simulado", respuesta.text)
        self.crear.assert_not_called()
        self.enviar.assert_not_called()

    def test_deja_consulta_y_envio_para_la_tarea_posterior(self):
        tareas = BackgroundTasks()

        respuesta = solicitar_recuperacion(
            SolicitudRecuperacion(correo="persona@example.com"),
            tareas,
            Response()
        )

        self.assertEqual(respuesta.mensaje, MENSAJE_RECUPERACION)
        self.assertEqual(len(tareas.tasks), 1)
        self.assertIs(tareas.tasks[0].func, procesar_solicitud_recuperacion)
        self.crear.assert_not_called()
        self.enviar.assert_not_called()

    def test_error_de_base_de_datos_no_revela_datos_sensibles(self):
        self.crear.side_effect = RuntimeError("Detalle privado de conexión")

        with self.assertLogs("app.routes.recuperacion_contrasena", level="ERROR") as logs:
            respuesta = self.cliente.post(
                "/auth/recuperar-contrasena",
                json={"correo": "persona@example.com"}
            )

        self.assertEqual(respuesta.status_code, 202)
        self.enviar.assert_not_called()
        self.assertNotIn("Detalle privado de conexión", " ".join(logs.output))
        self.assertNotIn("Detalle privado de conexión", respuesta.text)

    def test_error_de_envio_no_registra_correo_ni_tokens(self):
        token_microsoft = "access-token-microsoft-de-prueba"
        secreto = f"{self.solicitud.correo} {self.solicitud.token} {token_microsoft}"
        self.enviar.side_effect = RuntimeError(secreto)

        with self.assertLogs("app.routes.recuperacion_contrasena", level="ERROR") as logs:
            respuesta = self.cliente.post(
                "/auth/recuperar-contrasena",
                json={"correo": "persona@example.com"}
            )

        self.assertEqual(respuesta.status_code, 202)
        for dato in (
            self.solicitud.correo, self.solicitud.token, token_microsoft
        ):
            self.assertNotIn(dato, " ".join(logs.output))
            self.assertNotIn(dato, respuesta.text)


if __name__ == "__main__":
    unittest.main()
