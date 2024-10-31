import struct
import tempfile
import tkinter as tk
from character import Character
import ndspy.lz10
from PIL import Image, ImageTk
from pkb_file import unpack_pkb
from pac_file import unpack_pac

def center_window(window, width, height):
    # Obtener el tamaño de la pantalla
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calcular las coordenadas x e y para centrar la ventana
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    # Establecer la geometría de la ventana
    window.geometry(f'{width}x{height}+{x}+{y}')

def find_unitbase_file(rom, idCode):
    # Diccionario para mapear idCodes a rutas posibles del archivo unitbase.dat
    unitbase_paths = {
        "YEES": ["data_iz/logic/sp/unitbase.dat"],
        "YEEP": ["data_iz/logic/en/unitbase.dat"],
        "BEEP": ["data_iz/logic/en/unitbase.dat", "data_iz/logic/sp/unitbase.dat"],
        "BEES": ["data_iz/logic/sp/unitbase.dat"],
        "BOEJ": ["data_iz/logic/unitbase.dat"]
    }
    
    # Buscar el archivo unitbase.dat en las rutas posibles según el idCode
    for path in unitbase_paths.get(idCode, []):
        try:
            return rom.getFileByName(path)
        except ValueError:
            continue
    return None

def extract_characters_from_unitbase(content, sprites_list, models_list, rom):
    characters = {}

    # En caso de que el juego sea IE3, los parámetros serán diferentes
    if(rom.idCode.decode("ascii") == "BOEJ"):
        offset = 104
        name_length = 28
        next_player = 76
    
    else:
        offset = 96
        name_length = 32
        next_player = 64

    # Valor de name_bytes que indica que se debe detener la lectura
    stop_value = bytearray(b'\x96\xa2\x92\xe8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

    while offset + name_length <= len(content) and content[offset:offset + name_length]!=stop_value:
        # Comprobar si los bytes en offset+68 y offset+69 no son 00 00 y no son superiores a FF FF
        
        name_bytes = content[offset:offset + name_length]
        # Filtrar los bytes 00 y decodificar
        name = name_bytes.replace(b'\x00', b'').decode('ascii', errors='ignore').strip()

        if name:  # Solo añadir nombres no vacíos

            if(rom.idCode.decode("ascii") == "BOEJ"):
                # Obtenemos el id del personaje
                id = content[offset+79 : offset+81][::-1].hex()

                # Obtenemos el ID del sprite y modelo3D y lo pasamos a un formato que necesitamos para averiguar la ubicacion de los archivos
                sprite_model_ID = int(content[offset + 80:offset + 82][::-1].hex(), 16) * 100

                # Devolvemos finalmente la ubicacion exacta del sprite y modelo3D deseado en el juego
                sprite, modelo3D = find_model_sprite_location(sprite_model_ID, sprites_list, models_list)
                
                # Añadimos nuestro personaje con todos sus datos al diccionario
                pj = Character(id, name, sprite, modelo3D)
                characters[id] = pj

            else:
                # Obtenemos el id del personaje
                id = content[offset+66 : offset+68][::-1].hex()

                # Obtenemos el ID del sprite y modelo3D y lo pasamos a un formato que necesitamos para averiguar la ubicacion de los archivos
                sprite_model_ID = int(content[offset + 68:offset + 70][::-1].hex(), 16) * 100

                # Devolvemos finalmente la ubicacion exacta del sprite y modelo3D deseado en el juego
                sprite, modelo3D = find_model_sprite_location(sprite_model_ID, sprites_list, models_list)
                
                # Añadimos nuestro personaje con todos sus datos al diccionario
                pj = Character(id, name, sprite, modelo3D)
                characters[id] = pj

        offset += name_length+next_player
    
    

    return characters

def load_sprite_file(rom):
    sprite_file_path = "data_iz/face2d/fac.pkh"
    sprite_file = rom.getFileByName(sprite_file_path)
    sprites_list = []

    offset = 48

    while offset + 3 <= len(sprite_file):
        sprites_list.append(sprite_file[offset : offset+3].hex())
        offset+=12
    
    return sprites_list
    
def load_model_file(rom):
    model_file_path = "data_iz/model/char/pbf.pkh"
    model_file = rom.getFileByName(model_file_path)
    models_list = []

    offset = 48

    while offset + 3 <= len(model_file):
        models_list.append(model_file[offset : offset+3].hex())
        offset+=12
    
    return models_list

def load_sprites_images(rom):
    sprite_file_path = "data_iz/face2d/fac.pkb"
    sprite_file_path2 = "data_iz/face2d/fac.pkh"

    try:
        # Escribir los archivos PKB y PKH a archivos temporales
        pkb_temp_path = tempfile.mktemp()
        pkh_temp_path = tempfile.mktemp()
        
        with open(pkb_temp_path, 'wb') as pkb_temp_file:
            pkb_temp_file.write(rom.getFileByName(sprite_file_path))
        
        with open(pkh_temp_path, 'wb') as pkh_temp_file:
            pkh_temp_file.write(rom.getFileByName(sprite_file_path2))

        # Descomprimir el archivo PKB utilizando la función unpack_pkb
        return unpack_pkb(pkb_temp_path, pkh_temp_path)

    except Exception as e:
        print(f"Error loading sprite: {e}")


def find_model_sprite_location(sprite_model_ID, sprites_list, models_list):
    sprite_model_hex = sprite_model_ID.to_bytes(3, 'little').hex()

    try:    
        sprite_location = sprites_list.index(sprite_model_hex)     
    except ValueError:
        sprite_location = -1
    
    try:    
        model_location = models_list.index(sprite_model_hex)     
    except ValueError:
        model_location = -1

    return sprite_location, model_location
    

def display_names(characters, listbox):
    # Limpiar el Listbox antes de insertar nuevo contenido
    listbox.delete(0, tk.END)

    # Mostrar nombres únicos
    for character in characters.values():
        listbox.insert(tk.END, f"{character.nombre} ({character.id})")

def filter_names(event, listbox, characters):
    search_term = event.widget.get().lower()
    listbox.delete(0, tk.END)
    for character in characters.values():
        display_name = f"{character.nombre} ({character.id})"
        if search_term in character.nombre.lower():
            listbox.insert(tk.END, display_name)

def on_select(event, listbox, text_area, characters, canvas, sprites_images):
    # Obtener el índice seleccionado y mostrar el texto correspondiente
    selected_index = listbox.curselection()
    if selected_index:
        selected_entry = listbox.get(selected_index[0])
        # Extraer el ID del nombre seleccionado
        selected_id = selected_entry.split('(')[-1].split(')')[0]
        selected_character = characters[selected_id]
        text_area.delete('1.0', tk.END)

        if selected_character.sprite == -1:

            text_area.insert(tk.END, f"ID del personaje: {selected_character.id}\nSprite nº: No tiene\n3D Model nº: {selected_character.modelo_3d}\n\n")

        elif selected_character.modelo_3d == -1:

            text_area.insert(tk.END, f"ID: {selected_character.id}\nSprite nº: {selected_character.sprite}\n3D Model nº: No tiene\n\n")

            show_sprite_on_screen(selected_character.sprite, canvas, sprites_images)

        else:

            text_area.insert(tk.END, f"ID: {selected_character.id}\nSprite nº: {selected_character.sprite}\n3D Model nº: {selected_character.modelo_3d}\n\n")

            show_sprite_on_screen(selected_character.sprite, canvas, sprites_images)
    

def show_sprite_on_screen(sprite_number, canvas, sprites_images):
    try:
        # Encuentra el archivo PAC correspondiente al sprite_number
        pac_file = sprites_images[sprite_number]
        pac_data = pac_file['data']
        
        # Descomprimir los datos LZ10
        decompressed_data = ndspy.lz10.decompress(pac_data)

        decompressed_pack = unpack_pac(decompressed_data)

        # Obtener los datos de la paleta y los tiles
        palette_data = decompressed_pack[0]
        tile_data = decompressed_pack[2]

        # Crear la imagen utilizando la paleta y los datos de los tiles
        image = create_image_from_tiles_and_palette(tile_data['data'], palette_data['data'])

        # Mostrar la imagen en la ventana de Tkinter
        show_image_on_canvas(image, canvas)

    except Exception as e:
        print(f"Error showing sprite: {e}")


def create_image_from_tiles_and_palette(tile_data, palette_data, scale_factor=3):
     # Tamaño de la imagen original
    image_width = 64  # Ancho de la imagen original en píxeles
    image_height = 64  # Alto de la imagen original en píxeles

    # Tamaño de la imagen escalada
    scaled_width = image_width * scale_factor
    scaled_height = image_height * scale_factor

    # Asegúrate de que tile_data y palette_data tengan el tamaño esperado
    if len(palette_data) < 32:  # 16 colores * 2 bytes por color
        raise ValueError("Palette data is too short")
    
    if len(tile_data) < (image_width * image_height) // 2:  # Supongamos 4 bits por píxel
        raise ValueError("Tile data is too short")
    
    # Crear una imagen en blanco
    image = Image.new("RGBA", (image_width, image_height))

    # Convertir la paleta de colores a una lista de tuplas (R, G, B, A)
    palette = []
    for i in range(0, len(palette_data), 2):
        entry = palette_data[i:i+2]
        if i == 0:
            palette.append((0, 0, 0, 0))  # Transparente solo para el primer color
        else:
            entry_value = int.from_bytes(entry, 'little')
            r = (entry_value & 0x1F) << 3
            g = ((entry_value >> 5) & 0x1F) << 3
            b = ((entry_value >> 10) & 0x1F) << 3
            palette.append((r, g, b, 255))  # Opaco

    pixels = image.load()

    tile_index = 0
    for y in range(0, image_height, 8):  # Asumiendo tiles de 8x8 píxeles
        for x in range(0, image_width, 8):
            for row in range(8):
                for col in range(8 // 2):  # 4 bits por píxel
                    if tile_index >= len(tile_data):
                        raise IndexError("Tile data index out of range")
                    byte = tile_data[tile_index]
                    color_index_1 = byte & 0x0F
                    color_index_2 = (byte >> 4) & 0x0F
                    pixels[x + col * 2, y + row] = palette[color_index_1]
                    pixels[x + col * 2 + 1, y + row] = palette[color_index_2]
                    tile_index += 1
    
    # Escalar la imagen al tamaño deseado
    scaled_image = image.resize((scaled_width, scaled_height), Image.NEAREST)
    return scaled_image

def show_image_on_canvas(image, canvas):
    photo_image = ImageTk.PhotoImage(image)
    canvas.create_image(25, 220, anchor='nw', image=photo_image)
    canvas.image = photo_image  # Necesario para evitar que la imagen sea recolectada por el garbage collector
