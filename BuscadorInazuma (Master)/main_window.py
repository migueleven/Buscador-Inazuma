import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import ndspy.rom
import os, sys
from search_window import SearchWindow
from utils import center_window

### Main window where user can open and load a Inazuma Eleven NDS Game

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Buscador Inazuma")
        center_window(self.root, 800, 600)  # Centrar la ventana con tamaño 800x600
        
        # Deshabilitar la opción de redimensionar la ventana
        self.root.resizable(False, False)

        # Obtener la ruta del directorio actual del script
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        script_dir = os.path.join(base_path)

        # Establecer la ruta de la carpeta de imágenes
        self.image_dir = os.path.join(script_dir, 'images')

        # Establecer el icono de la aplicación
        self.icon_path = os.path.join(self.image_dir, 'icon.png')
        self.root.iconphoto(False, tk.PhotoImage(file=self.icon_path))

        # Crear el fondo
        background_path = os.path.join(self.image_dir, 'logo.png')
        self.background_image = Image.open(background_path)
        self.bg_image = ImageTk.PhotoImage(self.background_image)

        # Crear un Label separado para la imagen del logo2 y colocarlo en la parte superior
        self.logo_label = tk.Label(root, image=self.bg_image)
        self.logo_label.pack(side='top', pady=20)  # Ajusta 'pady' para dar espacio alrededor del logo

        # Label para mostrar la ruta del ROM seleccionado
        self.label_rom_path = tk.Label(root, text="No ROM selected", font=("Arial", 20, "bold"))
        self.label_rom_path.pack(pady=10)

        # Frame para contener los botones de imagen
        self.button_frame = tk.Frame(root, bd=5)
        self.button_frame.pack(pady=20)

        # Cargar la imagen del botón de abrir ROM
        open_rom_button_path = os.path.join(self.image_dir, 'open_rom_button.png')
        self.open_rom_image = Image.open(open_rom_button_path)
        self.open_rom_photo = ImageTk.PhotoImage(self.open_rom_image)

        # Cargar la imagen del botón de comenzar búsqueda
        start_search_button_path = os.path.join(self.image_dir, 'start_button.png')
        self.start_search_image = Image.open(start_search_button_path)
        self.start_search_photo = ImageTk.PhotoImage(self.start_search_image)

        # Botón de imagen para abrir el ROM
        self.btn_open_rom = tk.Button(self.button_frame, image=self.open_rom_photo, command=self.open_rom, borderwidth=0)
        self.btn_open_rom.pack(side='left', padx=10)

        # Botón de imagen para comenzar la búsqueda
        self.btn_start_search = tk.Button(self.button_frame, image=self.start_search_photo, command=self.start_search, state=tk.DISABLED, borderwidth=0)
        self.btn_start_search.pack(side='right', padx=10)

        # Crear un Label separado para la imagen del copyright y colocarlo en la parte inferior
        copy_path = os.path.join(self.image_dir, 'copy_image.png')
        self.open_copy_image = Image.open(copy_path)
        self.copy_image = ImageTk.PhotoImage(self.open_copy_image)
        self.logo_copy = tk.Label(root, image=self.copy_image)
        self.logo_copy.pack(side="bottom")
        self.logo_copy.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

        # Variable para almacenar los nombres originales
        self.names = []

        # Variable para almacenar la ruta de la rom
        self.rom_path = None

        # Variable rom del juego que se va a cargar
        self.rom = None

    def open_rom(self):
        # File Explorer, solo muestra archivos .nds
        rom_path = filedialog.askopenfilename(filetypes=[("NDS files", "*.nds")])
        if rom_path:
            self.rom = ndspy.rom.NintendoDSRom.fromFile(filePath=rom_path)  # Cargar el ROM

            # Validar que el código del juego contenga "INAZUMA11"
            if "INAZUMA11" not in str(self.rom.name):
                messagebox.showerror("Error", "La ROM seleccionada no es válida. Por favor, elija otra ROM.")
                return

            # Diccionario para mapear idCodes a mensajes
            self.idCode_messages = {
                "YEES": "Selected Game: Inazuma Eleven 1 (Spanish)",
                "YEEP": "Selected Game: Inazuma Eleven 1 (English)",
                "BEEP": "Selected Game: Inazuma Eleven 2",
                "BEES": "Selected Game: Inazuma Eleven 2 (Encrypted)",
                "BOEJ": "Selected Game: Inazuma Eleven 3 (Ogre)"
                # Agrega otros idCodes y mensajes según sea necesario
            }

            self.label_rom_path.config(text=self.idCode_messages[self.rom.idCode.decode("ascii")])  # Establecer la ruta del ROM en la etiqueta
            self.btn_start_search.config(state=tk.NORMAL)  # Habilitar el botón "Comenzar Búsqueda"

    def start_search(self):
        # Deshabilitar la ventana principal
        self.root.withdraw()

        # Crear una nueva ventana para los elementos de búsqueda y filtrado
        search_window = SearchWindow(self, self.rom)
        search_window.window.mainloop()
