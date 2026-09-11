# Counter nos ayuda a contar cuantas veces aparece cada vocal
# deque guarda solo las ultimas respuestas del programa
from collections import Counter, deque

# OpenCV se encarga de abrir la camara y mostrar la imagen
import cv2

# Traemos el detector de manos que contiene la logica de MediaPipe
from app.vision.detector import DetectorMano

# Traemos la funcion que revisa si la mano forma A, E, I, O o U
from app.vision.vocales import reconocer_vocal


# El numero 0 representa la camara principal del computador
INDICE_CAMARA = 0


# Cada pareja indica que dos puntos deben unirse con una linea
# Los numeros corresponden a los 21 puntos que detecta MediaPipe
CONEXIONES_MANO = [
    (0, 1), (1, 2), (2, 3), (3, 4),          # Pulgar
    (0, 5), (5, 6), (6, 7), (7, 8),          # Indice
    (5, 9), (9, 10), (10, 11), (11, 12),    # Medio
    (9, 13), (13, 14), (14, 15), (15, 16),  # Anular
    (13, 17), (17, 18), (18, 19), (19, 20), # Menique
    (0, 17),                                # Parte baja de la palma
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


def es_mano_derecha(resultado, posicion):
    # MediaPipe guarda si cada mano es derecha o izquierda
    # La posicion indica cual mano estamos revisando
    try:
        categoria = resultado.handedness[posicion][0]

        # La respuesta sera True solamente si aparece Right
        return categoria.category_name == "Right"

    # Si MediaPipe no puede decir que mano es devolvemos False
    except (AttributeError, IndexError, TypeError):
        return False


def estabilizar_vocal(vocal_actual):
    # Guardamos la vocal encontrada en este momento
    historial_vocales.append(vocal_actual)

    # Creamos una lista sin los valores None
    # None significa que no se reconocio ninguna vocal
    vocales_validas = [
        vocal for vocal in historial_vocales if vocal is not None
    ]

    # Si no tenemos ninguna vocal dejamos la pantalla sin letra
    if not vocales_validas:
        return None

    # Contamos las vocales guardadas
    # Luego elegimos la que mas se ha repetido
    vocal_mas_repetida, repeticiones = Counter(
        vocales_validas
    ).most_common(1)[0]

    # Mostramos la vocal solo si aparecio cuatro veces o mas
    if repeticiones >= 4:
        return vocal_mas_repetida

    # Si la vocal todavia no es segura no mostramos nada
    return None


def convertir_puntos_para_espejo(mano, ancho, alto):
    # MediaPipe entrega cada punto con valores entre 0 y 1
    # Aqui los pasamos a posiciones reales dentro de la ventana
    puntos = []

    # Recorremos los 21 puntos de la mano
    for punto in mano:

        # Invertimos x porque la imagen que mostramos funciona como espejo
        x = int((1.0 - punto.x) * ancho)

        # Multiplicamos y por el alto para conocer su posicion en la ventana
        y = int(punto.y * alto)

        # Guardamos las dos coordenadas del punto
        puntos.append((x, y))

    # Devolvemos la lista con los 21 puntos listos para dibujar
    return puntos


def dibujar_cuadro(imagen, mano, vocal):

    # imagen.shape nos entrega el alto y el ancho de la imagen
    alto, ancho, _ = imagen.shape

    # Convertimos los puntos de la mano a posiciones de la ventana
    puntos = convertir_puntos_para_espejo(
        mano,
        ancho,
        alto,
    )

    x_minimo = min(x for x, _ in puntos)
    y_minimo = min(y for _, y in puntos)
    x_maximo = max(x for x, _ in puntos)
    y_maximo = max(y for _, y in puntos)

    # Dejamos un pequeño espacio entre la mano y el cuadro
    margen = 25

    x_minimo = max(x_minimo - margen, 0)
    y_minimo = max(y_minimo - margen, 0)

    x_maximo = min(x_maximo + margen, ancho - 1)
    y_maximo = min(y_maximo + margen, alto - 1)

    # El cuadro sera verde cuando ya se reconocio una vocal
    # Mientras sigue revisando la mano sera amarillo
    color = (0, 220, 0) if vocal is not None else (0, 210, 255)

    cv2.rectangle(
        imagen,
        (x_minimo, y_minimo),
        (x_maximo, y_maximo),
        color,
        3,
    )


def dibujar_puntos(imagen, mano):

    # Obtenemos el tamaño de la imagen
    alto, ancho, _ = imagen.shape

    puntos = convertir_puntos_para_espejo(
        mano,
        ancho,
        alto,
    )

    # Recorremos las parejas de puntos que forman la mano
    for inicio, final in CONEXIONES_MANO:

        cv2.line(
            imagen,
            puntos[inicio],
            puntos[final],
            (0, 255, 0),
            2,
        )

    # Dibujamos los puntos detectados
    for punto in puntos:

        cv2.circle(
            imagen,
            punto,
            5,
            (0, 0, 255),
            -1,
        )


def dibujar_vocal(imagen, vocal):

    # Si no hay una vocal reconocida no dibujamos ninguna letra
    if vocal is None:
        return

    posicion = (30, 100)

    cv2.putText(
        imagen,
        vocal,
        posicion,
        cv2.FONT_HERSHEY_SIMPLEX,
        3,
        (0, 0, 0),
        10,
        cv2.LINE_AA,
    )

    cv2.putText(
        imagen,
        vocal,
        posicion,
        cv2.FONT_HERSHEY_SIMPLEX,
        3,
        (0, 220, 0),
        5,
        cv2.LINE_AA,
    )


def ejecutar():

    # Abrimos la camara usando la funcion creada
    camara = abrir_camara()

    # Guardamos el tiempo del cuadro anterior
    # MediaPipe necesita que cada nueva imagen tenga un tiempo mayor
    tiempo_anterior = 0


    try:

        # Creamos el detector reutilizable del modulo de vision
        detector = DetectorMano()


        while True:

            # Leemos una imagen de la camara
            disponible, imagen_original = camara.read()

            if not disponible:
                print("No se pudo obtener una imagen de la camara")
                break


            # OpenCV usa los colores en orden BGR
            # El detector se encarga de convertir la imagen
            tiempo_actual = int(
                cv2.getTickCount()
                / cv2.getTickFrequency()
                * 1000
            )


            if tiempo_actual <= tiempo_anterior:
                tiempo_actual = tiempo_anterior + 1


            tiempo_anterior = tiempo_actual


            # Enviamos la imagen al modulo de vision
            resultado = detector.detectar(
                imagen_original,
                tiempo_actual,
            )


            imagen_espejo = cv2.flip(
                imagen_original,
                1
            )


            mano_derecha = None


            # Buscamos la mano derecha detectada
            for posicion, mano in enumerate(resultado.hand_landmarks):

                if es_mano_derecha(resultado, posicion):

                    mano_derecha = mano
                    break


            if mano_derecha is not None:

                vocal_actual = reconocer_vocal(
                    mano_derecha
                )

                vocal_estable = estabilizar_vocal(
                    vocal_actual
                )


                dibujar_cuadro(
                    imagen_espejo,
                    mano_derecha,
                    vocal_estable,
                )


                dibujar_puntos(
                    imagen_espejo,
                    mano_derecha,
                )

            else:

                vocal_estable = estabilizar_vocal(None)


            dibujar_vocal(
                imagen_espejo,
                vocal_estable,
            )


            cv2.imshow(
                "Vocales LSC",
                imagen_espejo,
            )


            if cv2.waitKey(1) & 0xFF == ord("q"):
                break


    finally:

        # Dejamos de utilizar la camara
        camara.release()

        # Cerramos las ventanas creadas por OpenCV
        cv2.destroyAllWindows()



if __name__ == "__main__":

    try:

        ejecutar()


    except (FileNotFoundError, RuntimeError) as error:

        print(f"ERROR: {error}")