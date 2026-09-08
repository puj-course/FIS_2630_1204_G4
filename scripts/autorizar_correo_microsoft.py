import sys

from app.services.correo_recuperacion_service import (
    ConfiguracionCorreoError,
    obtener_configuracion_correo
)
from app.services.microsoft_oauth_service import (
    AutorizacionMicrosoftError,
    autorizar_cuenta_microsoft
)


def main() -> int:
    try:
        configuracion = obtener_configuracion_correo()
        autorizar_cuenta_microsoft(
            configuracion.client_id,
            configuracion.usuario,
            mostrar=lambda mensaje: print(mensaje, flush=True)
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
