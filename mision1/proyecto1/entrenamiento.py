# librerias
import re

"""
expresiones regulares en python
problemas reales 
"""

#codigo
print("libreria cargada correctamente")

#ejemplo 1 
texto="mi numero es 132"
resultado= re.search(r"\d+",texto)
print(f"{texto} Resultado {resultado.group()}")
texto="mi numero es 12345-985"
resultado=re.search(r"\d+",texto)
print(f"{texto}resultado{resultado.group()}")
texto="mi numero es 12345-985"
resultado=re.findall(r"\d+",texto)
print(f"{texto} resultado {resultado}")



documento= "cc.75.055.60"

def clean_id(documento):
    return re.sub(r"\D","",documento)
print(clean_id(documento))