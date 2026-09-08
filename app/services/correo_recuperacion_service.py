import os
import smtplib
import ssl
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.message import EmailMessage
from urllib.parse import urlencode, urlsplit, urlunsplit

from dotenv import load_dotenv
from email_validator import EmailNotValidError, validate_email


load_dotenv()


class ConfiguracionCorreoError(ValueError):
    pass


@dataclass(frozen=True)
class ConfiguracionCorreo:
    host: str
    puerto: int
    seguridad: str
    usuario: str = field(repr=False)
    contrasena: str = field(repr=False)
    remitente: str = field(repr=False)
    url_recuperacion: str


def obtener_configuracion_correo() -> ConfiguracionCorreo:
    host = os.getenv("SMTP_HOST", "").strip()
    usuario = os.getenv("SMTP_USER", "").strip()
    contrasena = os.getenv("SMTP_PASSWORD", "")
    remitente = os.getenv("SMTP_FROM", "").strip()
    url = os.getenv("RECUPERACION_URL", "").strip()
    seguridad = os.getenv("SMTP_SECURITY", "starttls").strip().lower()

    if not all((host, usuario, contrasena, remitente, url)):
        raise ConfiguracionCorreoError("Falta configurar el correo de recuperación")

    if seguridad not in ("starttls", "ssl"):
        raise ConfiguracionCorreoError("La conexión SMTP debe utilizar TLS")

    try:
        puerto = int(os.getenv("SMTP_PORT", "587"))
        if not 1 <= puerto <= 65535:
            raise ValueError

        remitente = validate_email(
            remitente,
            check_deliverability=False
        ).normalized
        partes = urlsplit(url)
        puerto_url = partes.port
    except (ValueError, EmailNotValidError) as error:
        raise ConfiguracionCorreoError("La configuración de correo no es válida") from error

    es_local = partes.hostname in ("localhost", "127.0.0.1", "::1")
    protocolo_valido = partes.scheme == "https" or (
        partes.scheme == "http" and es_local
    )

    if (
        not protocolo_valido
        or not partes.hostname
        or partes.username is not None
        or partes.password is not None
        or partes.query
        or partes.fragment
        or any(caracter.isspace() for caracter in url)
        or (puerto_url is not None and puerto_url == 0)
    ):
        raise ConfiguracionCorreoError("La URL de recuperación no es válida")

    return ConfiguracionCorreo(
        host=host,
        puerto=puerto,
        seguridad=seguridad,
        usuario=usuario,
        contrasena=contrasena,
        remitente=remitente,
        url_recuperacion=url
    )


def enviar_correo_recuperacion(
    correo: str,
    token: str,
    fecha_expiracion: datetime,
    configuracion: ConfiguracionCorreo
) -> None:
    partes = urlsplit(configuracion.url_recuperacion)
    # El fragmento lo leerá el frontend y no se envía al servidor al abrir la URL
    enlace = urlunsplit((
        partes.scheme,
        partes.netloc,
        partes.path,
        "",
        urlencode({"token": token})
    ))
    vencimiento = fecha_expiracion.astimezone(timezone.utc).strftime(
        "%Y-%m-%d %H:%M UTC"
    )

    mensaje = EmailMessage()
    mensaje["Subject"] = "Recuperación de contraseña de SignIA"
    mensaje["From"] = configuracion.remitente
    mensaje["To"] = correo
    mensaje.set_content(
        "Recibimos una solicitud para recuperar tu cuenta de SignIA.\n\n"
        "Abre este enlace para establecer una nueva contraseña:\n"
        f"{enlace}\n\n"
        f"El enlace vence el {vencimiento}.\n"
        "Si no solicitaste este cambio, puedes ignorar este mensaje.\n"
        "Tu contraseña actual todavía no ha cambiado.\n"
    )

    contexto_tls = ssl.create_default_context()

    if configuracion.seguridad == "ssl":
        cliente = smtplib.SMTP_SSL(
            configuracion.host,
            configuracion.puerto,
            timeout=10,
            context=contexto_tls
        )
    elif configuracion.seguridad == "starttls":
        cliente = smtplib.SMTP(
            configuracion.host,
            configuracion.puerto,
            timeout=10
        )
    else:
        raise ConfiguracionCorreoError("La conexión SMTP debe utilizar TLS")

    with cliente as servidor:
        if configuracion.seguridad == "starttls":
            servidor.ehlo()
            servidor.starttls(context=contexto_tls)
            servidor.ehlo()

        servidor.login(configuracion.usuario, configuracion.contrasena)
        rechazados = servidor.send_message(
            mensaje,
            from_addr=configuracion.remitente,
            to_addrs=[correo]
        )

        if rechazados:
            raise smtplib.SMTPRecipientsRefused(rechazados)
