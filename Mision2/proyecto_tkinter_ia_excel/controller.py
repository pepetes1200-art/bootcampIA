# controller.py
# Coordina la interfaz, la IA y la lógica de Excel

from ia_interpreter import interpretar_texto
from processor import ejecutar_accion


def procesar_instruccion(texto):
    try:
        instruccion = interpretar_texto(texto)
        ejecutar_accion(instruccion)
        return True, "Instrucción ejecutada correctamente"
    except Exception as e:
        return False, str(e)
