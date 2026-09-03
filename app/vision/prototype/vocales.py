# Funciones utilizadas para reconocer las vocales A, E, I, O y U de LSC

import math


# Se guardan los puntos principales de cada dedo detectados por MediaPipe
# Cada dedo contiene la base, dos articulaciones y la punta
PUNTOS_DEDOS = {
    "pulgar": (1, 2, 3, 4),
    "indice": (5, 6, 7, 8),
    "medio": (9, 10, 11, 12),
    "anular": (13, 14, 15, 16),
    "menique": (17, 18, 19, 20),
}


def distancia(punto_1, punto_2):

    # Calcula la distancia entre dos puntos de la mano
    # Se tienen en cuenta las posiciones x, y y z de cada punto

    # Se obtiene la diferencia entre las posiciones de los dos puntos
    diferencia_x = punto_1.x - punto_2.x
    diferencia_y = punto_1.y - punto_2.y
    diferencia_z = punto_1.z - punto_2.z

    # Se aplica la fórmula para encontrar la distancia entre los puntos
    return math.sqrt(
        diferencia_x ** 2
        + diferencia_y ** 2
        + diferencia_z ** 2
    )


def angulo(punto_1, vertice, punto_3):

    # Calcula el ángulo formado por tres puntos de la mano

    # Se crea la dirección desde el punto central hacia el primer punto
    vector_1 = (
        punto_1.x - vertice.x,
        punto_1.y - vertice.y,
        punto_1.z - vertice.z,
    )

    # Se crea la dirección desde el punto central hacia el tercer punto
    vector_2 = (
        punto_3.x - vertice.x,
        punto_3.y - vertice.y,
        punto_3.z - vertice.z,
    )

    # Se multiplican los valores de los dos vectores para comparar sus posiciones
    producto_punto = sum(
        valor_1 * valor_2
        for valor_1, valor_2 in zip(vector_1, vector_2)
    )

    # Se calcula el tamaño de cada vector
    norma_1 = math.sqrt(sum(valor ** 2 for valor in vector_1))
    norma_2 = math.sqrt(sum(valor ** 2 for valor in vector_2))

    # Se evita realizar una división cuando alguno de los vectores no tiene tamaño
    if norma_1 == 0 or norma_2 == 0:
        return 0

    # Se calcula el valor necesario para encontrar el ángulo
    coseno = producto_punto / (norma_1 * norma_2)

    # Se limita el valor para evitar errores pequeños en los decimales
    coseno = max(-1, min(1, coseno))

    # Se convierte el resultado de radianes a grados
    return math.degrees(math.acos(coseno))


def tamano_mano(mano):

    # Calcula una medida de referencia usando el tamaño de la mano

    # Se mide la distancia entre la muñeca y la base del dedo medio
    medida = distancia(mano[0], mano[9])

    # Se evita que la medida sea igual a cero
    return max(medida, 0.000001)


def distancia_relativa(mano, punto_1, punto_2):

    # Compara la distancia entre dos puntos teniendo en cuenta el tamaño de la mano

    # Se divide por el tamaño de la mano para que funcione aunque cambie la distancia
    # entre la mano y la cámara

    return distancia(
        mano[punto_1],
        mano[punto_2],
    ) / tamano_mano(mano)

def dedo_estirado(mano, nombre_dedo):

    # Comprueba si un dedo largo se encuentra completamente estirado

    # Se obtienen los puntos correspondientes al dedo que se quiere revisar
    base, articulacion_1, articulacion_2, punta = PUNTOS_DEDOS[
        nombre_dedo
    ]

    # Se calcula el primer ángulo del dedo
    angulo_1 = angulo(
        mano[base],
        mano[articulacion_1],
        mano[articulacion_2],
    )

    # Se calcula el segundo ángulo del dedo
    angulo_2 = angulo(
        mano[articulacion_1],
        mano[articulacion_2],
        mano[punta],
    )

    # Se considera que el dedo está estirado cuando sus articulaciones forman
    # ángulos cercanos a una línea recta
    return angulo_1 > 145 and angulo_2 > 145


def dedo_doblado(mano, nombre_dedo):

    # Comprueba si un dedo no cumple la condición de estar estirado

    # Se usa la función contraria para identificar un dedo doblado
    return not dedo_estirado(mano, nombre_dedo)


def pulgar_estirado(mano):

    # Comprueba si el pulgar está extendido hacia arriba

    # Se calcula el ángulo de la última parte del pulgar
    angulo_pulgar = angulo(mano[2], mano[3], mano[4])

    # Se revisa si la punta del pulgar está ubicada más arriba que la articulación
    apunta_arriba = mano[4].y < mano[3].y

    # Se considera estirado cuando está recto y apunta hacia arriba
    return angulo_pulgar > 145 and apunta_arriba


def indice_estirado(mano):

    # Comprueba si el dedo índice está estirado
    return dedo_estirado(mano, "indice")


def medio_estirado(mano):

    # Comprueba si el dedo medio está estirado
    return dedo_estirado(mano, "medio")


def anular_estirado(mano):

    # Comprueba si el dedo anular está estirado
    return dedo_estirado(mano, "anular")


def menique_estirado(mano):

    # Comprueba si el dedo meñique está estirado
    return dedo_estirado(mano, "menique")


def dedos_juntos(mano, dedo_1, dedo_2, limite=0.45):

    # Comprueba si las puntas de dos dedos están cerca entre sí

    # Se obtiene el punto de la punta de cada dedo
    punta_1 = PUNTOS_DEDOS[dedo_1][3]
    punta_2 = PUNTOS_DEDOS[dedo_2][3]

    # Se compara la distancia entre las puntas con el tamaño de la mano
    return distancia_relativa(
        mano,
        punta_1,
        punta_2,
    ) < limite

def forma_circular_o(mano):

    # Comprueba si la mano tiene la forma característica de la vocal O

    # Esta función calcula distancias usando solo las posiciones x y y
    # Se evita usar z porque puede variar más dependiendo de la cámara

    def distancia_2d_relativa(numero_punto_1, numero_punto_2):

        # Se obtienen los dos puntos que se van a comparar
        punto_1 = mano[numero_punto_1]
        punto_2 = mano[numero_punto_2]

        # Se calcula la diferencia entre las posiciones de los puntos
        diferencia_x = punto_1.x - punto_2.x
        diferencia_y = punto_1.y - punto_2.y

        # Se calcula la distancia entre los dos puntos
        distancia_entre_puntos = math.sqrt(
            diferencia_x ** 2
            + diferencia_y ** 2
        )

        # Se calcula el tamaño de referencia de la mano
        # tomando la distancia entre la muñeca y el dedo medio
        diferencia_mano_x = mano[0].x - mano[9].x
        diferencia_mano_y = mano[0].y - mano[9].y

        medida_mano = math.sqrt(
            diferencia_mano_x ** 2
            + diferencia_mano_y ** 2
        )

        # Se evita dividir entre cero si la medida de la mano no existe
        medida_mano = max(medida_mano, 0.000001)

        # Se devuelve la distancia comparada con el tamaño de la mano
        return distancia_entre_puntos / medida_mano

    # Se revisa que la punta del pulgar y la del índice estén juntas
    pulgar_toca_indice = distancia_2d_relativa(4, 8) < 0.35

    # Se revisa que las puntas de los dedos permanezcan agrupadas
    indice_medio_juntos = distancia_2d_relativa(8, 12) < 0.60

    medio_anular_juntos = distancia_2d_relativa(12, 16) < 0.60

    anular_menique_juntos = distancia_2d_relativa(16, 20) < 0.60

    # Se revisa que los dedos mantengan la separación necesaria
    # para formar el espacio interno de la vocal O
    indice_separado_de_base = distancia_2d_relativa(5, 8) > 0.40

    medio_separado_de_base = distancia_2d_relativa(9, 12) > 0.40

    return (
        pulgar_toca_indice
        and indice_medio_juntos
        and medio_anular_juntos
        and anular_menique_juntos
        and indice_separado_de_base
        and medio_separado_de_base
    )


def es_vocal_a(mano):

    # Comprueba si la posición de la mano corresponde a la vocal A

    # La vocal A tiene los dedos doblados y el pulgar extendido
    return (
        dedo_doblado(mano, "indice")
        and dedo_doblado(mano, "medio")
        and dedo_doblado(mano, "anular")
        and dedo_doblado(mano, "menique")
        and pulgar_estirado(mano)
    )


def es_vocal_e(mano):

    # Comprueba si la posición de la mano corresponde a la vocal E

    # La vocal E mantiene los dedos recogidos y el pulgar no está extendido
    return (
        dedo_doblado(mano, "indice")
        and dedo_doblado(mano, "medio")
        and dedo_doblado(mano, "anular")
        and dedo_doblado(mano, "menique")
        and not pulgar_estirado(mano)
        and not forma_circular_o(mano)
    )   

def es_vocal_i(mano):

    # Comprueba si la posición de la mano corresponde a la vocal I

    # La vocal I tiene únicamente el dedo meñique estirado
    return (
        dedo_doblado(mano, "indice")
        and dedo_doblado(mano, "medio")
        and dedo_doblado(mano, "anular")
        and menique_estirado(mano)
    )


def es_vocal_o(mano):

    # Comprueba si la posición de la mano corresponde a la vocal O

    # La vocal O tiene los dedos recogidos formando una figura circular
    # donde las puntas se acercan al pulgar
    return (
        dedo_doblado(mano, "indice")
        and dedo_doblado(mano, "medio")
        and dedo_doblado(mano, "anular")
        and dedo_doblado(mano, "menique")
        and forma_circular_o(mano)
    )


def es_vocal_u(mano):

    # Comprueba si la posición de la mano corresponde a la vocal U

    # La vocal U tiene el índice y el meñique extendidos
    return (
        indice_estirado(mano)
        and dedo_doblado(mano, "medio")
        and dedo_doblado(mano, "anular")
        and menique_estirado(mano)
    )


def reconocer_vocal(mano):

    # Revisa las condiciones de cada vocal y devuelve la encontrada

    # Se revisa primero la vocal O porque puede confundirse con una mano cerrada
    if es_vocal_o(mano):
        return "O"

    # Se revisa la vocal U porque tiene dos dedos extendidos
    if es_vocal_u(mano):
        return "U"

    # Se revisa la vocal I porque solamente tiene el meñique levantado
    if es_vocal_i(mano):
        return "I"

    # Se revisan A y E al final porque sus posiciones pueden ser parecidas
    if es_vocal_a(mano):
        return "A"

    if es_vocal_e(mano):
        return "E"

    # Se devuelve None cuando la posición no coincide con ninguna vocal
    return None
