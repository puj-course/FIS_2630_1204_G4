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

def es_letra_a(mano):
    indice_doblado = mano[8].y > mano[6].y
    medio_doblado = mano[12].y > mano[10].y
    anular_doblado = mano[16].y > mano[14].y
    menique_doblado = mano[20].y > mano[18].y

    tamaño_mano = distancia(mano[0], mano[9])
    distancia_pulgar = distancia(mano[4], mano[5])

    pulgar_cerca = distancia_pulgar < tamaño_mano * 0.9

    return (
        indice_doblado
        and medio_doblado
        and anular_doblado
        and menique_doblado
        and pulgar_cerca
    )

def es_letra_b(mano):
    indice_estirado = mano[8].y < mano[6].y
    medio_estirado = mano[12].y < mano[10].y
    anular_estirado = mano[16].y < mano[14].y
    menique_estirado = mano[20].y < mano[18].y
    pulgar_doblado = mano[4].y > mano[5].y

    tamaño_mano = distancia(mano[0], mano[9])


    indice_medio_juntos = (
        distancia(mano[8], mano[12]) < tamaño_mano * 0.55
    )

    medio_anular_juntos = (
        distancia(mano[12], mano[16]) < tamaño_mano * 0.55
    )

    anular_menique_juntos = (
        distancia(mano[16], mano[20]) < tamaño_mano * 0.55
    )


    return (
        indice_estirado
        and medio_estirado
        and anular_estirado
        and menique_estirado
        and pulgar_doblado
        and indice_medio_juntos
        and medio_anular_juntos 
        and anular_menique_juntos

    )


opciones = mp.tasks.vision.HandLandmarkerOptions(
    base_options=mp.tasks.BaseOptions(
        model_asset_path="hand_landmarker.task"
    ),
    running_mode=mp.tasks.vision.RunningMode.VIDEO,
    num_hands=1
)


camara = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not camara.isOpened():
    print("No se pudo abrir la camara.")
    exit()


with mp.tasks.vision.HandLandmarker.create_from_options(opciones) as detector:

    ultimo_tiempo = 0

    while True:
        disponible, imagen = camara.read()

        if not disponible:
            print("No se pudo obtener la imagen.")
            break

        # Voltea la imagen para que funcione como un espejo
        imagen = cv2.flip(imagen, 1)

        # OpenCV usa BGR y MediaPipe necesita RGB
        imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)

        imagen_mediapipe = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=imagen_rgb
        )

        tiempo_actual = int(time.monotonic() * 1000)

        if tiempo_actual <= ultimo_tiempo:
            tiempo_actual = ultimo_tiempo + 1

        ultimo_tiempo = tiempo_actual

        resultado = detector.detect_for_video(
            imagen_mediapipe,
            tiempo_actual
        )

        alto, ancho, _ = imagen.shape

        for mano in resultado.hand_landmarks:
            puntos = []

            for punto in mano:
                x = int(punto.x * ancho)
                y = int(punto.y * alto)

                puntos.append((x, y))

            # Dibuja las conexiones
            for inicio, fin in CONEXIONES:
                cv2.line(
                    imagen,
                    puntos[inicio],
                    puntos[fin],
                    (0, 255, 0),
                    2
                )

            # Dibuja los 21 puntos
            for punto in puntos:
                cv2.circle(imagen, punto, 5, (0, 0, 255), -1)

            cv2.putText(
                imagen,
                "Letra A" if es_letra_a(mano) else
                "Letra B" if es_letra_b(mano)
                else "Mano detectada",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

        cv2.imshow("Deteccion de manos", imagen)

        # Presiona la letra Q para cerrar
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


camara.release()
cv2.destroyAllWindows()