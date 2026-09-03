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

