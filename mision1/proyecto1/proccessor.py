import re
#========================================
# funcion celan_id
#  PUNTO elimina caracteres no numericos de un documento
#"cc75.88.56" = "758856"
# =======================================
def clean_id(value):
    # elimina carateres no numeros de un docummento
    if value is None:
        return""
    return re.sub(r"\D",'',str(value))
#========================================
#  funcion merge_name
#  une nombree y apellido en un solo campo
#====================================
def merge_name (name, lastname):
    if name is None:
        name=""
    if lastname is None:
        lastname=""
    return f"{name} {lastname}".strip()
        
        
            
            