import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from conf.database import obtener_conexion

LETRAS = [
    {"letra": "A", "descripcion": "La letra A en Lengua de Señas Colombiana se realiza formando un puño con los dedos cerrados sobre la palma de la mano, mientras el pulgar se apoya al costado del dedo índice, creando la configuración característica de esta letra.", "ruta_imagen": "assets/señas/LETRA A.jpg"},
    {"letra": "B", "descripcion": "La letra B en Lengua de Señas Colombiana se realiza con la mano abierta, los cuatro dedos extendidos y juntos hacia arriba, mientras el pulgar se dobla sobre la palma de la mano.", "ruta_imagen": "assets/señas/LETRA B.jpg"},
    {"letra": "C", "descripcion": "La letra C en Lengua de Señas Colombiana se representa curvando los dedos y el pulgar para formar la silueta de la letra C, dejando un espacio abierto entre ellos como si se sostuviera un objeto circular.", "ruta_imagen": "assets/señas/LETRA C.jpg"},
    {"letra": "D", "descripcion": "La letra D en Lengua de Señas Colombiana se realiza extendiendo el dedo índice hacia arriba mientras el pulgar y los demás dedos se unen formando un círculo en la base.", "ruta_imagen": "assets/señas/LETRA D.jpg"},
    {"letra": "E", "descripcion": "La letra E en Lengua de Señas Colombiana se realiza manteniendo los dedos flexionados hacia la palma de la mano, con el pulgar ubicado sobre ellos. Esta configuración representa la segunda vocal del alfabeto.", "ruta_imagen": "assets/señas/LETRA E.jpg"},
    {"letra": "F", "descripcion": "La letra F en Lengua de Señas Colombiana se representa uniendo las puntas del pulgar y el índice en un pequeño círculo, mientras los dedos medio, anular y meñique permanecen extendidos.", "ruta_imagen": "assets/señas/LETRA F.jpg"},
    {"letra": "G", "descripcion": "La letra G en Lengua de Señas Colombiana se realiza extendiendo el dedo índice y el pulgar de forma paralela y horizontal, manteniendo una pequeña separación entre ambos.", "ruta_imagen": "assets/señas/LETRA G.jpg"},
    {"letra": "H", "descripcion": "La letra H en Lengua de Señas Colombiana se representa extendiendo los dedos índice y medio juntos en posición horizontal, mientras el pulgar y los demás dedos permanecen cerrados.", "ruta_imagen": "assets/señas/LETRA H.jpg"},
    {"letra": "I", "descripcion": "La letra I en Lengua de Señas Colombiana se representa manteniendo los dedos cerrados sobre la palma de la mano y extendiendo únicamente el dedo meñique hacia arriba. Esta configuración corresponde a la tercera vocal del alfabeto.", "ruta_imagen": "assets/señas/LETRA I.jpg"},
    {"letra": "J", "descripcion": "La letra J en Lengua de Señas Colombiana parte de la configuración de la letra I, con el dedo meñique extendido, y se traza en el aire una trayectoria curva que representa el trazo de esta letra.", "ruta_imagen": "assets/señas/LETRA J.jpg"},
    {"letra": "K", "descripcion": "La letra K en Lengua de Señas Colombiana se realiza extendiendo los dedos índice y medio en forma de V, mientras el pulgar se apoya entre ambos dedos, tocando la base del dedo medio.", "ruta_imagen": "assets/señas/LETRA K.jpg"},
    {"letra": "L", "descripcion": "La letra L en Lengua de Señas Colombiana se representa extendiendo el dedo índice hacia arriba y el pulgar hacia el costado, formando un ángulo recto que asemeja la forma de la letra.", "ruta_imagen": "assets/señas/LETRA L.jpg"},
    {"letra": "M", "descripcion": "La letra M en Lengua de Señas Colombiana se realiza colocando el pulgar debajo de los dedos índice, medio y anular, los cuales se doblan hacia la palma cubriéndolo.", "ruta_imagen": "assets/señas/LETRA M.jpg"},
    {"letra": "N", "descripcion": "La letra N en Lengua de Señas Colombiana se realiza colocando el pulgar debajo de los dedos índice y medio, los cuales se doblan hacia la palma cubriéndolo.", "ruta_imagen": "assets/señas/LETRA N.jpg"},
    {"letra": "Ñ", "descripcion": "La letra Ñ en Lengua de Señas Colombiana parte de la configuración de la letra N, agregando un movimiento ondulante con la mano que representa la virgulilla característica de esta letra propia del español.", "ruta_imagen": "assets/señas/LETRA Ñ.jpg"},
    {"letra": "O", "descripcion": "La letra O en Lengua de Señas Colombiana se realiza uniendo las puntas de los dedos con el pulgar formando una figura circular. Esta configuración representa la forma de la letra O dentro del alfabeto.", "ruta_imagen": "assets/señas/LETRA O.jpg"},
    {"letra": "P", "descripcion": "La letra P en Lengua de Señas Colombiana se realiza con la misma configuración de la letra K, pero orientando la mano hacia abajo en lugar de hacia arriba.", "ruta_imagen": "assets/señas/LETRA P.jpg"},
    {"letra": "Q", "descripcion": "La letra Q en Lengua de Señas Colombiana se representa con la misma configuración de la letra G, pero orientando la mano hacia abajo en lugar de en posición horizontal hacia el frente.", "ruta_imagen": "assets/señas/LETRA Q.jpg"},
    {"letra": "R", "descripcion": "La letra R en Lengua de Señas Colombiana se realiza cruzando el dedo índice sobre el dedo medio, mientras los demás dedos permanecen cerrados.", "ruta_imagen": "assets/señas/LETRA R.jpg"},
    {"letra": "S", "descripcion": "La letra S en Lengua de Señas Colombiana se realiza formando un puño cerrado con el pulgar colocado sobre los demás dedos por delante.", "ruta_imagen": "assets/señas/LETRA S.jpg"},
    {"letra": "T", "descripcion": "La letra T en Lengua de Señas Colombiana se representa formando un puño cerrado con el pulgar ubicado entre el dedo índice y el dedo medio.", "ruta_imagen": "assets/señas/LETRA T.jpg"},
    {"letra": "U", "descripcion": "La letra U en Lengua de Señas Colombiana se representa manteniendo los dedos índice y medio extendidos y juntos, mientras los demás dedos permanecen cerrados. Esta configuración corresponde a la última vocal del alfabeto.", "ruta_imagen": "assets/señas/LETRA U.jpg"},
    {"letra": "V", "descripcion": "La letra V en Lengua de Señas Colombiana se realiza extendiendo los dedos índice y medio separados formando una V, mientras el pulgar y los demás dedos permanecen cerrados.", "ruta_imagen": "assets/señas/LETRA V.jpg"},
    {"letra": "W", "descripcion": "La letra W en Lengua de Señas Colombiana se representa extendiendo los dedos índice, medio y anular separados entre sí, mientras el pulgar sostiene el meñique doblado.", "ruta_imagen": "assets/señas/LETRA W.jpg"},
    {"letra": "X", "descripcion": "La letra X en Lengua de Señas Colombiana se realiza doblando el dedo índice en forma de gancho, mientras los demás dedos permanecen cerrados en el puño.", "ruta_imagen": "assets/señas/LETRA X.jpg"},
    {"letra": "Y", "descripcion": "La letra Y en Lengua de Señas Colombiana se realiza extendiendo el pulgar y el dedo meñique, mientras los dedos índice, medio y anular permanecen doblados hacia la palma.", "ruta_imagen": "assets/señas/LETRA Y.jpg"},
    {"letra": "Z", "descripcion": "La letra Z en Lengua de Señas Colombiana se representa extendiendo el dedo índice y trazando en el aire la forma de la letra Z, con los demás dedos cerrados.", "ruta_imagen": "assets/señas/LETRA Z.jpg"},
]

#FUNCION para llenar la BD con las 27 letras que usamos por el momento
def poblar_letras():
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            for item in LETRAS:
                cursor.execute(
                    """
                    INSERT INTO letras (letra, descripcion, ruta_imagen)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (letra) DO UPDATE SET
                        descripcion = EXCLUDED.descripcion,
                        ruta_imagen = EXCLUDED.ruta_imagen,
                        fecha_actualizacion = CURRENT_TIMESTAMP
                    """,
                    (item["letra"], item["descripcion"], item["ruta_imagen"]),
                )
        conexion.commit()
        print(f"Se procesaron {len(LETRAS)} letras.")
    except Exception as error:
        conexion.rollback()
        print(f"Error al poblar la tabla letras: {error}")
        raise
    finally:
        conexion.close()


if __name__ == "__main__":
    poblar_letras()

