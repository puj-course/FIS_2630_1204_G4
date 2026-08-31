import time
import cv2
import mediapipe as mp


# Conexiones entre los 21 puntos de la mano
CONEXIONES = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17)
]
def distancia(punto1, punto2):
    return (
        (punto1.x - punto2.x) ** 2
        + (punto1.y - punto2.y) ** 2
    ) ** 0.5
