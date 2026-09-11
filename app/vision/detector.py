from pathlib import Path

import mediapipe as mp


RUTA_MODELO = str(
    Path(__file__).resolve()
    .parent
    / "models"
    / "hand_landmarker.task"
)


class DetectorMano:

    def __init__(self):
        opciones = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path=RUTA_MODELO
            ),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.65,
            min_hand_presence_confidence=0.65,
            min_tracking_confidence=0.65,
        )

        self.detector = (
            mp.tasks.vision.HandLandmarker
            .create_from_options(opciones)
        )


    def detectar(self, imagen, tiempo_actual):
        return self.detector.detect_for_video(
            imagen,
            tiempo_actual
        )