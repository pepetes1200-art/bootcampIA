# ui.py
# Capa de interfaz gráfica (Tkinter)

import tkinter as tk
from tkinter import messagebox
from controller import procesar_instruccion


def iniciar_app():
    # Ventana principal
    root = tk.Tk()
    root.title("Procesador Excel con IA")
    root.geometry("500x300")

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
