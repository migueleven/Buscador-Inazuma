import os
import struct
import ndspy.rom
import tkinter as tk
from PIL import Image, ImageTk
import tempfile

### Class used to unpack and pack PKB files from NDS

class sFile:
    def __init__(self, name, offset, size, path):
        self.name = name
        self.offset = offset
        self.size = size
        self.path = path

class sFolder:
    def __init__(self):
        self.files = []

def unpack_pkb(pkb_path, pkh_path):
    with open(pkh_path, 'rb') as pkh_file:
        pkh_type = pkh_file.read(8).decode('ascii')
        if pkh_type == "PackNum ":
            return unpack_pkh1(pkb_path, pkh_path)
        else:
            return unpack_pkh2(pkb_path, pkh_path)

def unpack_pkh1(pkb_path, pkh_path):
    with open(pkh_path, 'rb') as pkh_file:
        pkh_file.seek(0x10)  # Skip the header name
        file_size = struct.unpack('<H', pkh_file.read(2))[0]
        pkh_type = struct.unpack('<H', pkh_file.read(2))[0]
        unknown = struct.unpack('<H', pkh_file.read(2))[0]
        num_files = struct.unpack('<H', pkh_file.read(2))[0]
        unknown2 = struct.unpack('<I', pkh_file.read(4))[0]
        block_length = struct.unpack('<I', pkh_file.read(4))[0]
        pkh_file.seek(pkh_file.tell() + 0x10)

        files = []
        if pkh_type == 0:
            for i in range(num_files):
                pkh_file.read(4)  # Unknown, ID?
                offset = struct.unpack('<I', pkh_file.read(4))[0]
                size = struct.unpack('<I', pkh_file.read(4))[0]
                files.append((offset, size))
        else:
            for i in range(num_files):
                pkh_file.read(4)  # Unknown, ID?
                offset = i * block_length
                size = block_length
                files.append((offset, size))

    with open(pkb_path, 'rb') as pkb_file:
        file_entries = []
        for i, (offset, size) in enumerate(files):
            pkb_file.seek(offset)
            data = pkb_file.read(size)
            file_entries.append({'name': f"{os.path.basename(pkb_path)}_{i}.pac_", 'data': data})

        return file_entries

def unpack_pkh2(pkb_path, pkh_path):
    with open(pkh_path, 'rb') as pkh_file:
        num_files = pkh_file.seek(0, os.SEEK_END) // 0x10
        pkh_file.seek(0)

        files = []
        for i in range(num_files):
            pkh_file.read(4)  # Unknown - ID?
            offset = struct.unpack('<I', pkh_file.read(4))[0]
            size = struct.unpack('<I', pkh_file.read(4))[0]
            pkh_file.read(4)  # First four bytes indicating the type of compression and the final size
            files.append((offset, size))

    with open(pkb_path, 'rb') as pkb_file:
        file_entries = []
        for i, (offset, size) in enumerate(files):
            pkb_file.seek(offset)
            data = pkb_file.read(size)
            file_entries.append({'name': f"{os.path.basename(pkb_path)}_{i}.pac_", 'data': data})

        return file_entries
