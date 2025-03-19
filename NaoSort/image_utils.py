import os
import shutil
from PIL import Image, UnidentifiedImageError

def is_animated(image_path):
    try:
        with Image.open(image_path) as img:
            return getattr(img, 'is_animated', False)
    except UnidentifiedImageError:
        return False

def move_to_gifs_folder(image_path, output_folder):
    gifs_folder = os.path.join(output_folder, "gifs")
    os.makedirs(gifs_folder, exist_ok=True)

    base_name = os.path.basename(image_path)
    target_path = os.path.join(gifs_folder, base_name)

    count = 1
    while os.path.exists(target_path):
        name, ext = os.path.splitext(base_name)
        target_path = os.path.join(gifs_folder, f"{name}_{str(count).zfill(4)}{ext}")
        count += 1

    shutil.move(image_path, target_path)
    print(f"Animierte Datei verschoben nach: {target_path}")

def convert_to_png(image_path):
    try:
        if image_path.lower().endswith(('.webp', '.jpg', '.jpeg')):
            with Image.open(image_path) as img:
                png_path = os.path.splitext(image_path)[0] + ".png"
                img.save(png_path, 'PNG')

                os.remove(image_path)  # Original löschen
                print(f"Originaldatei gelöscht: {image_path}")

                return png_path
        return image_path
    except Exception as e:
        print(f"Fehler bei der Konvertierung zu PNG: {e}")
        return None
