import struct
import os

### Class used to unpack and pack PAC files from NDS

def unpack_pac(data):
   try:
        if len(data) < 4:
            raise ValueError("El archivo PAC es demasiado pequeño para contener el número de archivos.")

        num_files = struct.unpack('<I', data[:4])[0]
        files = []
        offset = 4

        for _ in range(num_files):
            if offset + 8 > len(data):
                raise ValueError("El archivo PAC es demasiado pequeño para contener la cabecera del archivo.")

            file_offset = struct.unpack('<I', data[offset:offset+4])[0]
            file_size = struct.unpack('<I', data[offset+4:offset+8])[0]
            files.append((file_offset, file_size))
            offset += 8

        file_entries = []
        for i, (file_offset, file_size) in enumerate(files):
            if file_offset + file_size > len(data):
                raise ValueError(f"El archivo PAC es demasiado pequeño para contener los datos del archivo {i}.")

            file_data = data[file_offset:file_offset+file_size]
            file_entries.append({'name': f"file_{i}", 'data': file_data})

        return file_entries
   except Exception as e:
        print(f"Error unpacking PAC: {e}")
        return []
