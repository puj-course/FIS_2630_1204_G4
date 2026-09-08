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
    puntos = convertir_puntos_para_espejo(mano, ancho, alto)

    # Buscamos el punto que queda mas a la izquierda
    x_minimo = min(x for x, _ in puntos)

    # Buscamos el punto que queda mas arriba
    y_minimo = min(y for _, y in puntos)

    # Buscamos el punto que queda mas a la derecha
    x_maximo = max(x for x, _ in puntos)

    # Buscamos el punto que queda mas abajo
    y_maximo = max(y for _, y in puntos)

    # Dejamos un pequeño espacio entre la mano y el cuadro
    margen = 25

    # Restamos el margen del lado izquierdo sin salir de la imagen
    x_minimo = max(x_minimo - margen, 0)

    # Restamos el margen de la parte superior sin salir de la imagen
    y_minimo = max(y_minimo - margen, 0)

    # Sumamos el margen del lado derecho sin salir de la imagen
    x_maximo = min(x_maximo + margen, ancho - 1)

    # Sumamos el margen de la parte inferior sin salir de la imagen
    y_maximo = min(y_maximo + margen, alto - 1)

    # El cuadro sera verde cuando ya se reconocio una vocal
    # Mientras sigue revisando la mano sera amarillo
    color = (0, 220, 0) if vocal is not None else (0, 210, 255)

    # Dibujamos el cuadro alrededor de la mano
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

    # Preparamos los 21 puntos para dibujarlos sobre la imagen en espejo
    puntos = convertir_puntos_para_espejo(
        mano,
        ancho,
        alto,
    )

    # Recorremos las parejas de puntos que forman la mano
    for inicio, final in CONEXIONES_MANO:
        # Dibujamos una linea verde entre cada pareja
        cv2.line(
            imagen,
            puntos[inicio],
            puntos[final],
            (0, 255, 0),
            2,
        )

    # Recorremos nuevamente los 21 puntos
    for punto in puntos:
        # Dibujamos un circulo rojo en cada punto
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

    # Estas coordenadas colocan la vocal en la esquina superior izquierda
    posicion = (30, 100)

    # Primero dibujamos la letra en negro y un poco mas gruesa
    # Esta parte funciona como un borde para que la letra se pueda leer bien
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

    # Dibujamos la misma letra en verde encima del borde negro
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
    # Aqui configuramos la forma en la que trabajara MediaPipe
    opciones = mp.tasks.vision.HandLandmarkerOptions(
        # Indicamos donde se encuentra el archivo del detector de manos
        base_options=mp.tasks.BaseOptions(
            model_asset_path=RUTA_MODELO
        ),

        # VIDEO permite revisar continuamente las imagenes de la camara
        running_mode=mp.tasks.vision.RunningMode.VIDEO,

        # Solo queremos detectar una mano
        num_hands=1,

        # Estos tres valores controlan que tan segura debe ser la deteccion
        min_hand_detection_confidence=0.65,
        min_hand_presence_confidence=0.65,
        min_tracking_confidence=0.65,
    )

    # Abrimos la camara usando la funcion que creamos arriba
    camara = abrir_camara()

    # Guardamos el tiempo del cuadro anterior
    # MediaPipe necesita que cada nueva imagen tenga un tiempo mayor
    tiempo_anterior = 0

    try:
        # Creamos el detector usando las opciones anteriores
        with mp.tasks.vision.HandLandmarker.create_from_options(
            opciones
        ) as detector:

            # Este ciclo mantiene la camara funcionando
            while True:
                # Leemos una imagen de la camara
                disponible, imagen_original = camara.read()

                # Si no se pudo leer la imagen salimos del ciclo
                if not disponible:
                    print("No se pudo obtener una imagen de la camara")
                    break

                # OpenCV usa los colores en orden BGR
                # MediaPipe los necesita en orden RGB
                imagen_rgb = cv2.cvtColor(
                    imagen_original,
                    cv2.COLOR_BGR2RGB,
                )

                # Convertimos la imagen para que MediaPipe pueda recibirla
                imagen_mediapipe = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=imagen_rgb,
                )

                # Calculamos el tiempo actual en milisegundos
                tiempo_actual = int(
                    cv2.getTickCount()
                    / cv2.getTickFrequency()
                    * 1000
                )

                # Nos aseguramos de que el tiempo siempre avance
                if tiempo_actual <= tiempo_anterior:
                    tiempo_actual = tiempo_anterior + 1

                # Guardamos el tiempo para compararlo en la siguiente vuelta
                tiempo_anterior = tiempo_actual

                # Enviamos la imagen a MediaPipe para encontrar la mano
                resultado = detector.detect_for_video(
                    imagen_mediapipe,
                    tiempo_actual,
                )

                # Volteamos la imagen que se mostrara en la ventana
                # Esto hace que la camara se vea como un espejo
                imagen_espejo = cv2.flip(imagen_original, 1)

                # Al comenzar suponemos que todavia no encontramos la mano derecha
                mano_derecha = None

                # Recorremos las manos encontradas por MediaPipe
                for posicion, mano in enumerate(resultado.hand_landmarks):
                    # Revisamos si esta mano es la derecha
                    if es_mano_derecha(resultado, posicion):
                        # Guardamos la mano derecha y dejamos de buscar
                        mano_derecha = mano
                        break

                # Entramos aqui solamente cuando encontramos la mano derecha
                if mano_derecha is not None:
                    # Revisamos si la posicion de la mano coincide con una vocal
                    vocal_actual = reconocer_vocal(mano_derecha)

                    # Esperamos a que la vocal se repita para mostrarla
                    vocal_estable = estabilizar_vocal(vocal_actual)

                    # Dibujamos el cuadro alrededor de la mano
                    dibujar_cuadro(
                        imagen_espejo,
                        mano_derecha,
                        vocal_estable,
                    )

                    # Dibujamos los 21 puntos y las lineas que los unen
                    dibujar_puntos(
                        imagen_espejo,
                        mano_derecha,
                    )

                # Entramos aqui cuando no aparece la mano derecha
                else:
                    # Guardamos None para limpiar poco a poco el historial
                    vocal_estable = estabilizar_vocal(None)

                # Dibujamos la vocal reconocida en la esquina de la ventana
                dibujar_vocal(imagen_espejo, vocal_estable)

                # Mostramos la imagen terminada en una ventana
                cv2.imshow("Vocales LSC", imagen_espejo)

                # waitKey revisa si se presiono alguna tecla
                # El programa se cierra solamente cuando se presiona q
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    # Esta parte siempre se ejecuta aunque ocurra un error
    finally:
        # Dejamos de utilizar la camara
        camara.release()

        # Cerramos todas las ventanas creadas por OpenCV
        cv2.destroyAllWindows()


# Esta condicion permite ejecutar el programa desde este archivo
# Tambien evita que se inicie solo si algun dia lo importamos desde otro lugar
if __name__ == "__main__":
    try:
        # Iniciamos todo el programa
        ejecutar()

    # Si falta la camara o el modelo mostramos el error en la terminal
    except (FileNotFoundError, RuntimeError) as error:
        print(f"ERROR: {error}")
