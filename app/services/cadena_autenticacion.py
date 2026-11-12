from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone

from pwdlib.exceptions import UnknownHashError


class CuentaBloqueadaError(Exception):
    pass


@dataclass
class SolicitudAutenticacion:
    """Datos que recorren la cadena de autenticación."""

    correo: str
    # Se excluyen del repr para no exponer la contraseña ni el hash en registros
    contrasena: str = field(repr=False)
    usuario: dict | None = field(default=None, repr=False)


class ManejadorAutenticacion(ABC):
    """Eslabón de la cadena: rechaza la solicitud o la pasa al siguiente."""

    def __init__(self):
        self._siguiente: ManejadorAutenticacion | None = None

    def establecer_siguiente(
        self,
        manejador: "ManejadorAutenticacion"
    ) -> "ManejadorAutenticacion":
        self._siguiente = manejador
        return manejador

    @abstractmethod
    def manejar(self, solicitud: SolicitudAutenticacion) -> dict | None:
        raise NotImplementedError

    def _pasar_al_siguiente(
        self,
        solicitud: SolicitudAutenticacion
    ) -> dict | None:
        # Sin un eslabón final que autentique, la cadena rechaza por defecto
        if self._siguiente is None:
            return None

        return self._siguiente.manejar(solicitud)


class ManejadorUsuarioExistente(ManejadorAutenticacion):
    """Rechaza la solicitud si no existe un usuario con el correo."""

    def __init__(self, obtener_usuario_por_correo):
        super().__init__()
        self._obtener_usuario_por_correo = obtener_usuario_por_correo

    def manejar(self, solicitud: SolicitudAutenticacion) -> dict | None:
        solicitud.usuario = self._obtener_usuario_por_correo(solicitud.correo)

        if solicitud.usuario is None:
            return None

        return self._pasar_al_siguiente(solicitud)


class ManejadorCuentaNoBloqueada(ManejadorAutenticacion):
    """Detiene la autenticación si la cuenta sigue bloqueada."""

    def manejar(self, solicitud: SolicitudAutenticacion) -> dict | None:
        bloqueado_hasta = solicitud.usuario["bloqueado_hasta"]

        if (
            bloqueado_hasta is not None
            and bloqueado_hasta > datetime.now(timezone.utc)
        ):
            raise CuentaBloqueadaError(
                "La cuenta está bloqueada temporalmente"
            )

        return self._pasar_al_siguiente(solicitud)


class ManejadorContrasena(ManejadorAutenticacion):
    """Último eslabón: verifica la contraseña y devuelve el usuario público."""

    def __init__(
        self,
        password_hash,
        registrar_intento_fallido,
        reiniciar_intentos_fallidos
    ):
        super().__init__()
        self._password_hash = password_hash
        self._registrar_intento_fallido = registrar_intento_fallido
        self._reiniciar_intentos_fallidos = reiniciar_intentos_fallidos

    def manejar(self, solicitud: SolicitudAutenticacion) -> dict | None:
        usuario = solicitud.usuario

        try:
            contrasena_correcta = self._password_hash.verify(
                solicitud.contrasena,
                usuario["contrasena_hash"]
            )
        except UnknownHashError:
            contrasena_correcta = False

        if not contrasena_correcta:
            self._registrar_intento_fallido(usuario["id_usuario"])
            return None

        self._reiniciar_intentos_fallidos(usuario["id_usuario"])

        return {
            "id_usuario": usuario["id_usuario"],
            "nombre": usuario["nombre"],
            "correo": usuario["correo"],
            "rol": usuario["rol"]
        }