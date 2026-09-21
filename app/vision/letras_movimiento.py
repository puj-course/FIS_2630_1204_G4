from pathlib import Path

ruta = Path("app/vision/letras_movimiento.py")
texto = ruta.read_text(encoding="utf-8")

inicio = texto.index("    # Ñ:")
final = texto.index("    return None", inicio)

nuevo = '''    # S: configuración cerrada y recorrido curvo en ambos ejes.
    if (
        dedos_principales_doblados
        and resumen_muneca.cambios_direccion_x >= 2
        and resumen_muneca.rango_x >= 0.45
        and resumen_muneca.rango_y >= 0.45
        and resumen_muneca.recorrido_total >= 1.2
    ):
        return "S"

    # Ñ: configuración cerrada con oscilación horizontal.
    if (
        dedos_principales_doblados
        and resumen_muneca.cambios_direccion_x >= 1
        and resumen_muneca.rango_x >= 0.45
        and resumen_muneca.rango_y <= 0.45
    ):
        return "Ñ"

'''

ruta.write_text(
    texto[:inicio] + nuevo + texto[final:],
    encoding="utf-8",
)
