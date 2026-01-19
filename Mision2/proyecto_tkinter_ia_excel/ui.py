# ui.py
# Capa de interfaz gráfica (Tkinter)

import tkinter as tk
from tkinter import messagebox,filedialog
from controller import procesar_instruccion
from processor import process_excel_safe



def seleccionar_excel():
    title="selecioandor archivo excel",
    return filedialog.askopenfilename(
    title="seleccionar arvicho excel",
    filetypes= [("archivo excel","*.xlsx")]
    )
def on_clic_procesar():
    archivo = seleccionar_excel()
    exito,mensaje=process_excel_safe("path")
    if exito:
        messagebox.showinfo("proceso completado",mensaje)
    else:
        messagebox.showerror("error",mensaje)
def iniciar_app():
    root = tk.Tk()
    root.title ("procesador de archivos excel")
    root.geometry("400x400")
    root.resizable(False,False)
    
    boton = tk.Button(
        root,
        text="selecionar archivo de excel",
        command=on_clic_procesar,
        width=30,
        height=2
        
    )
    boton.pack(pady=60)
    root.mainloop()

def iniciar_app():
    # Ventana principal
    root = tk.Tk()
    root.title("Procesador Excel con IA")
    root.geometry("400x400")

    tk.Button( root,
        text="selecionar archivo de excel",
        command=on_clic_procesar,
        width=30,
        height=2).pack(pady=60)
    # Etiqueta
    tk.Label(root, text="Escriba una instrucción en lenguaje natural").pack(pady=10)

    # Campo de texto
    entrada = tk.Entry(root, width=60)
    entrada.pack(pady=5)

    # Acción del botón
    def ejecutar():
        texto = entrada.get()
        exito, mensaje = procesar_instruccion(texto)

        if exito:
            messagebox.showinfo("Resultado", mensaje)
        else:
            messagebox.showerror("Error", mensaje)

    # Botón
    tk.Button(root, text="Ejecutar instrucción", command=ejecutar).pack(pady=20)

    root.mainloop()
