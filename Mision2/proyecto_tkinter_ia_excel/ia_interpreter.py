# ia_interpreter.py
# Simula una IA básica usando reglas y expresiones regulares

import re


def interpretar_texto(texto):
    texto = texto.lower()

    # Limpieza de columna por letra
    if "limpia" in texto and "columna" in texto:
        col = re.search(r"columna\s+([a-z])", texto)
        if col:
            return {"action": "clean_id", "column": col.group(1).upper()}

    # Unión de nombre y apellido
    if "une" in texto and "nombre" in texto:
        return {
            "action": "merge_name",
            "name_column": "Nombre",
            "last_column": "Apellido",
            "target": "NombreCompleto"
        }

    raise ValueError("No se pudo interpretar la instrucción")
