from pathlib import Path

import cv2
import mediapipe as mp

RUTA_MODELO = str(
    Path(__file__).resolve()
    .parent
    / "models"
    / "hand_landmarker.task"
)


class DetectorMano:

    def __init__(self, modo_video: bool = True):

        # Guarda el modo de procesamiento
        self.modo_video = modo_video

        modo = (
            mp.tasks.vision.RunningMode.VIDEO
            if modo_video
            else mp.tasks.vision.RunningMode.IMAGE
        )

        # Configura el detector
        opciones = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path=RUTA_MODELO
            ),
            running_mode=modo,
            num_hands=1,
            min_hand_detection_confidence=0.65,
            min_hand_presence_confidence=0.65,
            min_tracking_confidence=0.65,
        )

        # Carga el modelo
        self.detector = (
            mp.tasks.vision.HandLandmarker
            .create_from_options(opciones)
        )

    def detectar(
        self,
        imagen,
        tiempo_actual: int | None = None,
    ):

        # Convierte los colores de la imagen
        imagen_rgb = cv2.cvtColor(
            imagen,
            cv2.COLOR_BGR2RGB,
        )

        # Prepara la imagen para MediaPipe
        imagen_mediapipe = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=imagen_rgb,
        )

        # Procesa un fotograma de video
        if self.modo_video:
            if tiempo_actual is None:
                raise ValueError(
                    "El modo video requiere un tiempo en milisegundos"
                )

            return self.detector.detect_for_video(
                imagen_mediapipe,
                tiempo_actual,
            )

        # Procesa una imagen independiente
        return self.detector.detect(imagen_mediapipe)

    def cerrar(self):

        # Libera los recursos del detector
        self.detector.close()