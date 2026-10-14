from abc import ABC, abstractmethod
from threading import Lock

from app.vision.detector import DetectorMano


class GestorDetectores(ABC):
    """Contrato para procesar imágenes y liberar los detectores."""

    @abstractmethod
    def detectar(
        self,
        imagen,
        tiempo_actual: int | None = None,
    ):
        raise NotImplementedError

    @abstractmethod
    def cerrar(self) -> None:
        raise NotImplementedError


class GestorDetectoresCompartido(GestorDetectores):
    """Singleton que administra los detectores dentro de un proceso."""

    _instancia = None
    _bloqueo_instancia = Lock()

    def __new__(cls):
        with cls._bloqueo_instancia:
            if cls._instancia is None:
                instancia = super().__new__(cls)
                instancia._detectores = {}
                instancia._bloqueo_operaciones = Lock()
                cls._instancia = instancia

            return cls._instancia

    def detectar(
        self,
        imagen,
        tiempo_actual: int | None = None,
    ):
        # El tiempo determina el modo del detector de MediaPipe.
        modo_video = tiempo_actual is not None

        # Protege la creación y el uso frente a llamadas concurrentes.
        with self._bloqueo_operaciones:
            if modo_video not in self._detectores:
                self._detectores[modo_video] = DetectorMano(
                    modo_video=modo_video,
                )

            detector = self._detectores[modo_video]

            return detector.detectar(
                imagen,
                tiempo_actual,
            )

    def cerrar(self) -> None:
        # Impide cerrar un detector mientras procesa una imagen.
        with self._bloqueo_operaciones:
            for detector in self._detectores.values():
                detector.cerrar()

            self._detectores.clear()