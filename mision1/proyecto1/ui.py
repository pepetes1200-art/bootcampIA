#https://docs.python.org/es/3/library/tkinter.html#
import tkinter as tk
from tkinter import filedialog ,messagebox
from proccessor import process_excel_safe


def seleccionar_excel():
    title="selecioandor archivo excel",
    return filedialog.askopenfilename(
    title="seleccionar arvicho excel",
    filetypes= [("archivo excel","*.xlsx")]
    )
def on_clic_procesar():
    archivo = seleccionar_excel()
    exito,mensaje=process_excel_safe(archivo)
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