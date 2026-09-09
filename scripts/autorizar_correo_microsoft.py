import argparse
import platform
import sys

from app.services.correo_recuperacion_service import (
    ConfiguracionCorreoError,
    obtener_configuracion_correo
)
from app.services.microsoft_oauth_service import (
    AutorizacionMicrosoftError,
    autorizar_cuenta_microsoft,
    crear_persistencia_microsoft
)


def main(argumentos=None) -> int:
    parser = argparse.ArgumentParser(description="Autorizar el correo de SignIA")
    parser.add_argument(
        "--comprobar", action="store_true",
        help="Revisar configuración y acceso inicial al almacén seguro sin iniciar sesión"
    )
    opciones = parser.parse_args(argumentos)
    try:
        configuracion = obtener_configuracion_correo()
        if opciones.comprobar:
            persistencia = crear_persistencia_microsoft(
                configuracion.client_id, configuracion.usuario, configuracion.transporte
            )
            print(f"Envío: {configuracion.transporte}")
            print(f"Sistema: {platform.system()} / {platform.machine()}")
            print(f"Almacén seguro: {type(persistencia).__name__}")
            print("Configuración y almacenamiento inicializados correctamente.")
            print("Pendiente: autorizar la cuenta y comprobar un envío real.")
            return 0
        autorizar_cuenta_microsoft(
            configuracion.client_id,
            configuracion.usuario,
            mostrar=lambda mensaje: print(mensaje, flush=True),
            transporte=configuracion.transporte
        )
    except (ConfiguracionCorreoError, AutorizacionMicrosoftError) as error:
        print(str(error), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Autorización cancelada.", file=sys.stderr)
        return 1
    except Exception as error:
        print(
            f"No fue posible completar la autorización ({type(error).__name__}).",
            file=sys.stderr
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
