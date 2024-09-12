import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageStat
import random

imagen = None
imagen_mosaico = None  # Variable para almacenar la imagen generada

# Funciones de escalamiento y color promedio
def escalar(imagen, factor):
    ancho_original, alto_original = imagen.size
    nuevo_ancho = int(ancho_original * factor)
    nuevo_alto = int((nuevo_ancho / ancho_original) * alto_original)
    return imagen.resize((nuevo_ancho, nuevo_alto))

def color_promedio(imagen):
    stat = ImageStat.Stat(imagen)
    return tuple(map(int, stat.mean[:3]))

def random_color():
    return tuple([random.randint(0, 255) for _ in range(3)])

# Función para crear la imagen recursiva
def crear_imagen_recursiva(imagen, factor_medida=2, factor_escala=0.02, guardar_tonos=False):
    # Imagen reducida
    imagen_reducida = escalar(imagen, factor_escala)
    
    # Imagen aumentada
    imagen_aumentada = escalar(imagen, factor_medida)

    # Dimensiones de la subimagen
    sub_ancho, sub_alto = imagen_reducida.size

    # Dimensiones de la imagen final
    ancho, alto = imagen_aumentada.size

    # Crear una imagen en blanco para colocar los bloques
    imagen_recursiva = Image.new('RGB', (ancho, alto))

    # Calcular el número total de bloques
    tonos = {}

    # Bloques totales
    total_bloques_x = ancho // sub_ancho
    total_bloques_y = alto // sub_alto
    total_bloques = total_bloques_x * total_bloques_y

    bloques_procesados = 0

    # Recorrer la imagen en bloques
    for x in range(0, ancho, sub_ancho):
        for y in range(0, alto, sub_alto):
            # Definir el área del bloque
            area = (x, y, x + sub_ancho, y + sub_alto)

            # Obtenemos una parte de la imagen aumentada
            bloque = imagen_aumentada.crop(area)

            # Calcular color promedio del bloque
            tono = color_promedio(bloque)

            # Si no hemos creado la imagen con el tono de color, la creamos
            clave = str(tono)
            if clave not in tonos:
                mica = Image.new('RGB', (sub_ancho, sub_alto), tono)
                imagen_con_mica = Image.blend(imagen_reducida, mica, alpha=0.5)
                tonos[clave] = imagen_con_mica

            # Pegamos el bloque coloreado
            imagen_recursiva.paste(tonos[clave], (x, y))

            # Actualizar barra de progreso
            bloques_procesados += 1
            actualizar_barra(bloques_procesados, total_bloques)

    return imagen_recursiva

# Funciones para la interfaz gráfica
def cargar_imagen():
    global imagen
    file_path = filedialog.askopenfilename(
        filetypes=[("Archivos de imagen", "*.jpg;*.jpeg;*.png;*.bmp;*.tiff")]
    )
    if file_path:
        imagen = Image.open(file_path)
        mostrar_imagen(imagen)

def mostrar_imagen(imagen):
    imagen.thumbnail((400, 400))  # Redimensiona la imagen para ajustarse al espacio
    imagen_tk = ImageTk.PhotoImage(imagen)
    label_img.config(image=imagen_tk)
    label_img.image = imagen_tk

def aplicar_mosaico():
    global imagen, imagen_mosaico
    if imagen:
        try:
            # Restablecer la barra de progreso
            barra_progreso['value'] = 0

            # Generar imagen recursiva
            factor_medida = 2  # Factor de medida para la imagen final
            factor_escala = 0.02  # Factor de escalado de las subimágenes
            imagen_mosaico = crear_imagen_recursiva(imagen, factor_medida, factor_escala)
            mostrar_imagen(imagen_mosaico)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al aplicar el mosaico: {e}")
    else:
        messagebox.showwarning("Advertencia", "Primero debes cargar una imagen.")

def guardar_imagen():
    global imagen_mosaico
    if imagen_mosaico:
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")])
        if file_path:
            imagen_mosaico.save(file_path)
            messagebox.showinfo("Guardar Imagen", "Imagen guardada correctamente.")
    else:
        messagebox.showwarning("Advertencia", "Primero debes generar la imagen para poder guardarla.")

def actualizar_barra(bloques_procesados, total_bloques):
    progreso = (bloques_procesados / total_bloques) * 100
    barra_progreso['value'] = progreso
    ventana.update_idletasks()

# Configuración de la interfaz gráfica con Tkinter
ventana = tk.Tk()
ventana.title("Angel en Color")

ancho_pantalla = ventana.winfo_screenwidth()
alto_pantalla = ventana.winfo_screenheight()

ancho_ventana = 800
alto_ventana = 600

posicion_x = (ancho_pantalla - ancho_ventana) // 2
posicion_y = (alto_pantalla - alto_ventana) // 2

ventana.geometry(f"{ancho_ventana}x{alto_ventana}+{posicion_x}+{posicion_y}")

label_img = tk.Label(ventana)
label_img.pack()

# Frame para alinear los botones en horizontal
frame_botones = tk.Frame(ventana)
frame_botones.pack(pady=20)

# Botón para cargar la imagen
boton_cargar = tk.Button(frame_botones, text="Cargar Imagen", command=cargar_imagen)
boton_cargar.pack(side=tk.LEFT, padx=10)

# Botón para aplicar el mosaico con el color promedio
boton_mosaico = tk.Button(frame_botones, text="Mosaico Recursivo a Color", command=aplicar_mosaico)
boton_mosaico.pack(side=tk.LEFT, padx=10)

# Botón para guardar la imagen generada
boton_guardar = tk.Button(frame_botones, text="Guardar Imagen", command=guardar_imagen)
boton_guardar.pack(side=tk.LEFT, padx=10)

# Barra de progreso
barra_progreso = ttk.Progressbar(ventana, orient="horizontal", length=400, mode="determinate")
barra_progreso.pack(pady=20)

# Loop de ventana principal
ventana.mainloop()
