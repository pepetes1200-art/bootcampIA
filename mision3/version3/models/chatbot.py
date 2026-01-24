import os 


)
chat_completion = client.chat.completions.create(
     model="llama-3.3-70b-versatile",
    messages=[
        {
            "role":"system",
            "content":(
                "ere un experto en Microsoft excel y analisis de datos. "
                "tu tarea es interpretar instrucciones en lenguaje natural"
                "y extrae la instruccion  del usuario. \n\n"
                "debes identificar:\n"
                "- la accion principal (sumar, filtrar, ordenar, agrupar, etc. )\n"
                "- las columnas involucradas \n"
                "- las condiciones si existen\n"
                "Devuelve siempre la respuesta en formato JSON con esta estructura:\n"
                "{\n"
                ' "accion":"",\n'
                ' "columnas":[],\n'
                '"condiciones:[],\n'
                '"resultado":""\n'
                "}"
            )
        },
        {
            "role":"user",
            "content":"Quiero sumar las ventas por vendedor solo del año 2024"
        }
    ],

)
print(chat_completion.choices[0].message.content)