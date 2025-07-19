import os
import shutil
from send2trash import send2trash

def copy_file(src, dst):
    shutil.copy2(src, dst)

def delete_path(path):
    send2trash(path)

def rename_path(old_path, new_path):
    os.rename(old_path, new_path)

def create_folder(path):
    os.makedirs(path, exist_ok=True)
