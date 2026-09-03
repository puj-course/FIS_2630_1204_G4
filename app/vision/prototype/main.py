# Counter nos ayuda a contar cuantas veces aparece cada vocal
# deque guarda solo las ultimas respuestas del programa
from collections import Counter, deque

# OpenCV se encarga de abrir la camara y mostrar la imagen
import cv2

# MediaPipe encuentra los 21 puntos de la mano
import mediapipe as mp

# Traemos la funcion que revisa si la mano forma A, E, I, O o U
from vocales import reconocer_vocal


# Este es el archivo que MediaPipe usa para detectar la mano
RUTA_MODELO = "hand_landmarker.task"

# El numero 0 representa la camara principal del computador
INDICE_CAMARA = 0

# Cada pareja indica que dos puntos deben unirse con una linea
# Los numeros corresponden a los 21 puntos que detecta MediaPipe
CONEXIONES_MANO = [
    (0, 1), (1, 2), (2, 3), (3, 4),          # Pulgar
    (0, 5), (5, 6), (6, 7), (7, 8),          # Indice
    (5, 9), (9, 10), (10, 11), (11, 12),     # Medio
    (9, 13), (13, 14), (14, 15), (15, 16),   # Anular
    (13, 17), (17, 18), (18, 19), (19, 20),  # Menique
    (0, 17),                                  # Parte baja de la palma
]

# Aqui se guardan las ultimas cinco vocales que reconoce el programa
# Esto evita que la letra cambie demasiado rapido en la pantalla
historial_vocales = deque(maxlen=5)


def abrir_camara():
    # Primero intentamos abrir la camara con la opcion de Windows
    camara = cv2.VideoCapture(INDICE_CAMARA, cv2.CAP_DSHOW)

    # Si no funciona de esa forma cerramos ese intento
    # Luego dejamos que OpenCV intente abrirla automaticamente
    if not camara.isOpened():
        camara.release()
        camara = cv2.VideoCapture(INDICE_CAMARA)

    # Si la camara sigue cerrada detenemos el programa
    if not camara.isOpened():
        raise RuntimeError("No se pudo abrir la camara")

    # Elegimos el ancho que queremos para la imagen
    camara.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)

    # Elegimos el alto que queremos para la imagen
    camara.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # Devolvemos la camara para poder usarla en el resto del programa
    return camara

