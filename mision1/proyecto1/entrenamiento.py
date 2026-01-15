# liberarias
import re

"""
expresiones  regulares en python
problemas reales 
"""

# codigos 
print("libreria cargada correctamente")
# ejemplo
texto="mi numero es 12345"
resultado=re.search(r"\d+",texto)
print(resultado.group())