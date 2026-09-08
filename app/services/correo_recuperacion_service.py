import os
import smtplib
import ssl
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.message import EmailMessage
from urllib.parse import urlencode, urlsplit, urlunsplit
from uuid import UUID

from dotenv import load_dotenv
from email_validator import EmailNotValidError, validate_email

from app.services.microsoft_oauth_service import obtener_token_microsoft


load_dotenv()


class ConfiguracionCorreoError(ValueError):
    pass


@dataclass(frozen=True)
class ConfiguracionCorreo:
    host: str
    puerto: int
    seguridad: str
    usuario: str = field(repr=False)
    client_id: str
    remitente: str = field(repr=False)
    url_recuperacion: str


def obtener_configuracion_correo() -> ConfiguracionCorreo:
    host = os.getenv("SMTP_HOST", "").strip()
    usuario = os.getenv("SMTP_USER", "").strip()
    client_id = os.getenv("MICROSOFT_CLIENT_ID", "").strip()
    remitente = os.getenv("SMTP_FROM", "").strip()
    url = os.getenv("RECUPERACION_URL", "").strip()
    seguridad = os.getenv("SMTP_SECURITY", "starttls").strip().lower()

    if not all((host, usuario, client_id, remitente, url)):
        raise ConfiguracionCorreoError("Falta configurar el correo de recuperación")

    if host.lower() != "smtp-mail.outlook.com" or seguridad != "starttls":
        raise ConfiguracionCorreoError(
            "Para Hotmail utiliza smtp-mail.outlook.com y STARTTLS"
        )

    try:
        puerto = int(os.getenv("SMTP_PORT", "587"))
        if puerto != 587:
            raise ValueError

        client_id = str(UUID(client_id))
        usuario = validate_email(usuario, check_deliverability=False).normalized.lower()

        remitente = validate_email(
            remitente,
            check_deliverability=False
        ).normalized.lower()
        if usuario != remitente:
            raise ValueError
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
        host=host.lower(),
        puerto=puerto,
        seguridad=seguridad,
        usuario=usuario,
        client_id=client_id,
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

    if (
        configuracion.host != "smtp-mail.outlook.com"
        or configuracion.puerto != 587
        or configuracion.seguridad != "starttls"
    ):
        raise ConfiguracionCorreoError("La configuración SMTP de Microsoft no es válida")

    token_microsoft = obtener_token_microsoft(
        configuracion.client_id,
        configuracion.usuario
    )

    def autenticar(reto=None):
        if reto is not None:
            return ""
        return f"user={configuracion.usuario}\x01auth=Bearer {token_microsoft}\x01\x01"

    with smtplib.SMTP(configuracion.host, configuracion.puerto, timeout=10) as servidor:
        servidor.ehlo()
        servidor.starttls(context=ssl.create_default_context())
        servidor.ehlo()
        servidor.auth("XOAUTH2", autenticar)
        rechazados = servidor.send_message(
            mensaje,
            from_addr=configuracion.remitente,
            to_addrs=[correo]
        )

        if rechazados:
            raise smtplib.SMTPRecipientsRefused(rechazados)
