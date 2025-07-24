import re

def dividir_texto_en_bloques(texto, max_longitud=500):
    import re
    oraciones = re.split(r'(?<=[.!?])\s+', texto)
    bloques = []
    bloque_actual = ""
    for oracion in oraciones:
        if len(bloque_actual) + len(oracion) < max_longitud:
            bloque_actual += oracion + " "
        else:
            bloques.append(bloque_actual.strip())
            bloque_actual = oracion + " "
    if bloque_actual:
        bloques.append(bloque_actual.strip())
    return bloques
