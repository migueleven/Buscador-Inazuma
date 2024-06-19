import tkinter as tk
from PIL import Image, ImageTk
import os
from utils import *
import character


class SearchWindow:
    def __init__(self, main_app, rom):
        self.main_app = main_app
        self.rom = rom
        self.window = tk.Toplevel(self.main_app.root)
        self.window.title("Buscador Inazuma")
        center_window(self.window, 1066, 600)

        # Deshabilitar la opción de redimensionar la ventana
        self.window.resizable(False, False)

        # Enlazar el evento de cierre de la ventana secundaria para que llame a back_to_main
        self.window.protocol("WM_DELETE_WINDOW", lambda: self.back_to_main(self.window))

        # Establecer el icono de la aplicación
        self.icon_path = os.path.join(self.main_app.image_dir, 'icono2.png')
        self.window.iconphoto(False, tk.PhotoImage(file=self.icon_path))

        self.canvas = tk.Canvas(self.window, width=1066, height=600)
        self.canvas.pack()

        # Añadir una imagen de fondo en la nueva ventana
        search_background_path = os.path.join(self.main_app.image_dir, 'fondo3.png')  # Ruta a la imagen de fondo de la nueva ventana
        self.search_background_image = Image.open(search_background_path)
        self.search_bg_image = ImageTk.PhotoImage(self.search_background_image)
        self.bg = self.canvas.create_image(0, 0, image=self.search_bg_image, anchor="nw")

        # Listbox para mostrar los nombres extraídos
        self.listbox = tk.Listbox(self.window, width=45, height=20, borderwidth=2, relief="solid")
        self.listbox.place(relx=0.39, rely=0.52, anchor='center')
        self.listbox.bind('<<ListboxSelect>>', lambda event: on_select(event, self.listbox, self.text_area, characters, self.canvas, sprites_images))

        # Text widget para mostrar el texto correspondiente al nombre seleccionado
        self.text_area = tk.Text(self.window, wrap=tk.WORD, width=45, height=20, borderwidth=2, relief="solid")
        self.text_area.place(relx=0.815, rely=0.67, anchor='center')

        # Entry para buscar nombres
        self.search_entry = tk.Entry(self.window, borderwidth=3, highlightthickness=0, width=28, bg='#ffffff')
        self.search_entry.place(relx=0.39, rely=0.22, anchor='center')
        self.search_entry.bind('<KeyRelease>', lambda event: filter_names(event, self.listbox, characters))

        # Cargar la imagen del botón de volver
        btn_back_image_path = os.path.join(self.main_app.image_dir, 'back_button.png')
        self.back_image = Image.open(btn_back_image_path)
        self.back_button_photo = ImageTk.PhotoImage(self.back_image)
        self.btn_back = self.canvas.create_image(500, 550, image=self.back_button_photo)
        self.canvas.tag_bind(self.btn_back, "<Button-1>", lambda event: self.back_to_main(self.window))

        # Colecciones donde guardaremos los datos
        characters = {}
        sprites_file = []
        models_file = []

        # Obtener el contenido de unitbase.dat y guardar personajes en diccionario
        unitbase_content = find_unitbase_file(self.rom, self.rom.idCode.decode("ascii"))
        sprites_file = load_sprite_file(self.rom)
        models_file = load_model_file(self.rom)
        sprites_images = load_sprites_images(self.rom)

        characters = extract_characters_from_unitbase(unitbase_content, sprites_file, models_file, self.rom)

        # Mostrar nombres de los personajes leidos
        display_names(characters, self.listbox)

    def back_to_main(self, window):
        window.destroy()
        self.main_app.root.deiconify()