import os
import smtplib
import ssl
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.message import EmailMessage
from urllib.parse import urlencode, urlsplit, urlunsplit
from uuid import UUID

import httpx

from dotenv import load_dotenv
from email_validator import EmailNotValidError, validate_email

from app.services.microsoft_oauth_service import obtener_token_microsoft


load_dotenv()


class ConfiguracionCorreoError(ValueError):
    pass


class EnvioMicrosoftGraphError(RuntimeError):
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
    transporte: str = "smtp"


def obtener_configuracion_correo() -> ConfiguracionCorreo:
    transporte = os.getenv("CORREO_TRANSPORTE", "smtp").strip().lower()
    if transporte not in ("smtp", "graph"):
        raise ConfiguracionCorreoError("CORREO_TRANSPORTE debe ser smtp o graph")

    host = os.getenv("SMTP_HOST", "").strip()
    usuario = os.getenv("SMTP_USER", "").strip()
    client_id = os.getenv("MICROSOFT_CLIENT_ID", "").strip()
    remitente = os.getenv("SMTP_FROM", "").strip()
    url = os.getenv("RECUPERACION_URL", "").strip()
    seguridad = os.getenv("SMTP_SECURITY", "starttls").strip().lower()

    if not all((usuario, client_id, remitente, url)) or (transporte == "smtp" and not host):
        raise ConfiguracionCorreoError("Falta configurar el correo de recuperación")

    if transporte == "smtp" and (host.lower() != "smtp-mail.outlook.com" or seguridad != "starttls"):
        raise ConfiguracionCorreoError(
            "Para Hotmail utiliza smtp-mail.outlook.com y STARTTLS"
        )

    try:
        puerto = int(os.getenv("SMTP_PORT", "587")) if transporte == "smtp" else 587
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
        url_recuperacion=url,
        transporte=transporte
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

    if configuracion.transporte == "graph":
        token_microsoft = obtener_token_microsoft(
            configuracion.client_id, configuracion.usuario, transporte="graph"
        )
        try:
            respuesta = httpx.post(
                "https://graph.microsoft.com/v1.0/me/sendMail",
                headers={"Authorization": f"Bearer {token_microsoft}"},
                json={
                    "message": {
                        "subject": str(mensaje["Subject"]),
                        "body": {
                            "contentType": "Text",
                            "content": mensaje.get_content()
                        },
                        "toRecipients": [{"emailAddress": {"address": correo}}]
                    }
                },
                timeout=10,
                follow_redirects=False
            )
        except httpx.RequestError:
            raise EnvioMicrosoftGraphError(
                "No fue posible conectar con Microsoft Graph"
            ) from None
        if respuesta.status_code != 202:
            raise EnvioMicrosoftGraphError(
                f"Microsoft Graph rechazó el envío (HTTP {respuesta.status_code})"
            )
        return

    if configuracion.transporte != "smtp":
        raise ConfiguracionCorreoError("El transporte de correo no es válido")

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
