import hashlib
import sys
from pathlib import Path
from uuid import UUID

import msal
from msal_extensions import (
    CrossPlatLock,
    PersistedTokenCache,
    build_encrypted_persistence
)


AUTORIDAD_MICROSOFT = "https://login.microsoftonline.com/consumers"
PERMISOS_CORREO = ["https://outlook.office.com/SMTP.Send"]


class AutorizacionMicrosoftError(RuntimeError):
    pass


def crear_persistencia_microsoft(client_id: str, correo: str):
    identificador = str(UUID(client_id))
    cuenta = hashlib.sha256(correo.strip().lower().encode("utf-8")).hexdigest()
    carpeta = Path.home() / ".signia" / "microsoft" / identificador
    carpeta.mkdir(parents=True, exist_ok=True, mode=0o700)
    ubicacion = carpeta / f"{cuenta}.bin"

    try:
        persistencia = build_encrypted_persistence(str(ubicacion))
        if not persistencia.is_encrypted:
            raise AutorizacionMicrosoftError("El almacenamiento debe estar cifrado")
        return persistencia
    except Exception as error:
        ayuda = {
            "win32": (
                "En Windows, ejecuta la autorización y el backend con la misma "
                "cuenta de Windows; la caché está protegida por DPAPI."
            ),
            "darwin": (
                "En macOS, desbloquea el llavero de inicio de sesión y permite "
                "el acceso de Python a Keychain cuando el sistema lo solicite."
            ),
            "linux": (
                "En Linux se necesita libsecret, PyGObject dentro de .venv "
                "y una sesión de escritorio con el llavero desbloqueado."
            )
        }.get(sys.platform, "Utiliza Windows, macOS o Linux con almacenamiento cifrado.")
        raise AutorizacionMicrosoftError(
            "No fue posible abrir el almacén seguro del sistema. " + ayuda
        ) from error


def crear_aplicacion_microsoft(client_id: str, cache):
    return msal.PublicClientApplication(
        client_id=str(UUID(client_id)),
        authority=AUTORIDAD_MICROSOFT,
        token_cache=cache,
        timeout=10
    )


def obtener_token_microsoft(client_id: str, correo: str) -> str:
    persistencia = crear_persistencia_microsoft(client_id, correo)
    cache = PersistedTokenCache(
        persistencia,
        lock_location=persistencia.get_location() + ".lock"
    )
    aplicacion = crear_aplicacion_microsoft(client_id, cache)
    cuentas = aplicacion.get_accounts(username=correo.strip().lower())

    if len(cuentas) != 1:
        raise AutorizacionMicrosoftError(
            "La cuenta remitente no está autorizada. Ejecuta "
            "python -m scripts.autorizar_correo_microsoft"
        )

    # MSAL reutiliza el token o lo renueva sin iniciar un flujo interactivo
    resultado = aplicacion.acquire_token_silent(
        scopes=PERMISOS_CORREO,
        account=cuentas[0]
    )
    token = resultado.get("access_token") if resultado else None

    if not isinstance(token, str) or not token:
        raise AutorizacionMicrosoftError(
            "La autorización de Microsoft requiere iniciar sesión otra vez. "
            "Ejecuta python -m scripts.autorizar_correo_microsoft"
        )

    return token


def autorizar_cuenta_microsoft(client_id: str, correo: str, mostrar=print) -> None:
    persistencia = crear_persistencia_microsoft(client_id, correo)
    cache_temporal = msal.SerializableTokenCache()
    aplicacion = crear_aplicacion_microsoft(client_id, cache_temporal)
    flujo = aplicacion.initiate_device_flow(scopes=PERMISOS_CORREO)

    if not flujo.get("user_code") or not flujo.get("verification_uri"):
        raise AutorizacionMicrosoftError(
            "Microsoft no permitió iniciar la autorización. Revisa el ID de "
            "aplicación, las cuentas personales y los flujos de cliente público."
        )

    mostrar(f"Abre {flujo['verification_uri']} en tu navegador.")
    mostrar(f"Introduce este código: {flujo['user_code']}")
    mostrar(f"Inicia sesión con la cuenta remitente: {correo}")
    mostrar("Comprueba el nombre de tu aplicación y acepta el permiso de envío.")
    resultado = aplicacion.acquire_token_by_device_flow(flujo)

    if not resultado or not resultado.get("access_token"):
        codigos = resultado.get("error_codes", []) if resultado else []
        codigos = [str(codigo) for codigo in codigos if type(codigo) is int]
        detalle = f" Código de Microsoft: {', '.join(codigos)}." if codigos else ""
        raise AutorizacionMicrosoftError(
            "La autorización no se completó. Puede haber vencido el código "
            "o haberse rechazado el permiso." + detalle
        )

    # Solo se guarda la autorización si pertenece a la cuenta configurada
    cuentas = aplicacion.get_accounts(username=correo.strip().lower())
    if len(cuentas) != 1:
        raise AutorizacionMicrosoftError(
            "La cuenta autorizada no coincide con SMTP_USER. Utiliza su "
            "dirección principal en SMTP_USER y SMTP_FROM y vuelve a autorizar."
        )

    with CrossPlatLock(persistencia.get_location() + ".lock"):
        persistencia.save(cache_temporal.serialize())

    mostrar("Cuenta Microsoft autorizada correctamente. No se ha enviado ningún correo.")
