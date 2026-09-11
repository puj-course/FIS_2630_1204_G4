import unittest

from pydantic import ValidationError

from src.schemas.recuperacion import (
    RespuestaRecuperacion,
    SolicitudRecuperacion
)


class TestSolicitudRecuperacion(unittest.TestCase):
    def test_acepta_correo_valido(self):
        solicitud = SolicitudRecuperacion(correo="persona@example.com")

        self.assertEqual(solicitud.correo, "persona@example.com")

    def test_normaliza_espacios_y_mayusculas(self):
        solicitud = SolicitudRecuperacion(correo="  Persona@Example.COM  ")

        self.assertEqual(solicitud.correo, "persona@example.com")

    def test_rechaza_correo_ausente(self):
        with self.assertRaises(ValidationError):
            SolicitudRecuperacion()

    def test_rechaza_correos_invalidos(self):
        correos = (
            "",
            "   ",
            "persona",
            "persona@",
            "@example.com",
            "persona@@example.com",
            "persona@example",
            "per sona@example.com",
            "persona..otra@example.com",
            "persona@\r\nexample.com"
        )

        for correo in correos:
            with self.subTest(correo=correo):
                with self.assertRaises(ValidationError):
                    SolicitudRecuperacion(correo=correo)

    def test_rechaza_valores_no_textuales(self):
        for valor in (None, 123, True, [], {}):
            with self.subTest(valor=valor):
                with self.assertRaises(ValidationError):
                    SolicitudRecuperacion(correo=valor)

    def test_acepta_limite_de_150_caracteres(self):
        correo = "a" * 64 + "@" + "b" * 63 + "." + "c" * 17 + ".com"

        self.assertEqual(len(correo), 150)
        self.assertEqual(SolicitudRecuperacion(correo=correo).correo, correo)

    def test_rechaza_mas_de_150_caracteres(self):
        correo = "a" * 64 + "@" + "b" * 63 + "." + "c" * 18 + ".com"

        self.assertEqual(len(correo), 151)

        with self.assertRaises(ValidationError):
            SolicitudRecuperacion(correo=correo)

    def test_rechaza_campos_adicionales(self):
        for campo, valor in (
            ("id_usuario", 1),
            ("rol", "administrador"),
            ("token", "token-de-prueba")
        ):
            with self.subTest(campo=campo):
                with self.assertRaises(ValidationError):
                    SolicitudRecuperacion.model_validate({
                        "correo": "persona@example.com",
                        campo: valor
                    })


class TestRespuestaRecuperacion(unittest.TestCase):
    def test_respuesta_solo_contiene_mensaje(self):
        respuesta = RespuestaRecuperacion(mensaje="Solicitud recibida")

        self.assertEqual(
            respuesta.model_dump(),
            {"mensaje": "Solicitud recibida"}
        )

    def test_respuesta_rechaza_datos_adicionales(self):
        with self.assertRaises(ValidationError):
            RespuestaRecuperacion.model_validate({
                "mensaje": "Solicitud recibida",
                "token": "token-de-prueba"
            })


if __name__ == "__main__":
    unittest.main()
