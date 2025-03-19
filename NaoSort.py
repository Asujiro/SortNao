import os
import re
import shutil
import time
from PIL import Image, UnidentifiedImageError
import requests

class SauceNao:
    def __init__(self, api_key, output_folder, temp_folder):
        self.api_key = api_key
        self.endpoint = "https://saucenao.com/search.php"
        self.output_folder = output_folder
        self.temp_folder = temp_folder  # Ordner fÃ¼r temporÃ¤re Dateien
        self.rate_limit_time = 30
        self.processed_files = set()

    def is_animated(self, image_path):
        try:
            with Image.open(image_path) as img:
                return getattr(img, 'is_animated', False)
        except UnidentifiedImageError:
            return False

    def move_to_gifs_folder(self, image_path):
        gifs_folder = os.path.join(self.output_folder, "gifs")
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

    def convert_to_png(self, image_path):
        try:
            if image_path.lower().endswith(('.webp', '.jpg', '.jpeg')):
                with Image.open(image_path) as img:
                    png_path = os.path.splitext(image_path)[0] + ".png"
                    img.save(png_path, 'PNG')

                    os.remove(image_path)  # Original lÃ¶schen
                    print(f"Originaldatei gelÃ¶scht: {image_path}")

                    return png_path
            return image_path  # Falls schon PNG, wird sie direkt verwendet
        except Exception as e:
            print(f"Fehler bei der Konvertierung zu PNG: {e}")
            return None

    def request(self, image_path):
        image_path = self.convert_to_png(image_path) or image_path

        try:
            with open(image_path, 'rb') as file:
                files = {'file': ('file.png', file, 'image/png')}
                data = {'api_key': self.api_key, 'output_type': '2', 'db': '9', 'numres': '16'}

                response = requests.post(self.endpoint, files=files, data=data)

                if response.status_code == 200:
                    return self.parse_response(response.json()), image_path
                elif response.status_code == 429:
                    self.handle_rate_limit(image_path)  # Rate Limit erreicht
                else:
                    print(f"Fehler beim Abrufen der Daten: {response.status_code}")
                    return None, image_path
        except Exception as e:
            print(f"Fehler bei der Anfrage: {e}")
            return None, image_path
        
    def handle_rate_limit(self, image_path):
        print("Rate Limit erreicht! Speichere Datei zwischen...")
        
        # Hier speichern wir die PNG-Datei im temporÃ¤ren Ordner
        temp_path = os.path.join(self.temp_folder, os.path.basename(image_path))
        shutil.move(image_path, temp_path)  # Konvertierte PNG wird verschoben
        print(f"Bild zwischengespeichert: {temp_path}")

        print("Warte 24 Stunden...")
        time.sleep(86400)  # Wartezeit bei Rate Limit

        # Versuche es erneut, die Datei zu verarbeiten
        self.request(temp_path)

    def parse_response(self, response):
        results = response.get('results', [])

        highest_similarity = 0
        best_character = None

        for result in results:
            similarity = float(result.get('header', {}).get('similarity', 0))
            characters = result.get('data', {}).get('characters', None)

            if similarity < 50 or not characters:
                continue

            character_name = characters.split(',')[0].strip()

            if similarity > highest_similarity:
                highest_similarity = similarity
                best_character = character_name

        if best_character:
            print(f"Erkannter Charakter: {best_character} ({highest_similarity}%)")
            return best_character
        else:
            print("Nichts erkannt - Bild wird als 'unknown' einsortiert.")
            return "Unbekannter Charakter"

    def clean_folder_name(self, name):
         # Ersetze alle ungÃ¼ltigen Zeichen (auÃŸer Klammern) durch "_"
        cleaned_name = re.sub(r'[\\/:*?"<>|()]', '', name)  # Entfernt Klammern und ungÃ¼ltige Zeichen
        
        cleaned_name = cleaned_name.replace(" ", "_")

        # Vermeide doppelte "_" (falls mehr als ein "_" hintereinander erscheint)
        cleaned_name = re.sub(r'_{2,}', '_', cleaned_name)
        
        
        # Entferne "_" am Ende des Namens
        if cleaned_name.endswith('_'):
            cleaned_name = cleaned_name[:-1]
        
        
        return cleaned_name


    def move_image(self, image_path, character_name):
        # Bereinige den Ordnernamen
        folder_name = "unknown" if character_name == "Unbekannter Charakter" else self.clean_folder_name(character_name)
        target_folder = os.path.join(self.output_folder, folder_name)
        os.makedirs(target_folder, exist_ok=True)

        base_name = os.path.basename(image_path)
        target_path = os.path.join(target_folder, base_name)

        count = 1
        while os.path.exists(target_path):
            name, ext = os.path.splitext(base_name)
            target_path = os.path.join(target_folder, f"{name}_{str(count).zfill(4)}{ext}")
            count += 1

        shutil.move(image_path, target_path)
        print(f"Bild verschoben nach: {target_path}")

    def process_images_from_folder(self, folder_path):
        # Verarbeite temporÃ¤r gespeicherte Bilder zuerst
        temp_image_paths = [os.path.join(self.temp_folder, f) for f in os.listdir(self.temp_folder)
                            if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        for temp_image_path in temp_image_paths:
            print(f"Verarbeite temporÃ¤re Datei: {temp_image_path}")
            character_name, final_image_path = self.request(temp_image_path)
            self.move_image(final_image_path, character_name or "Unbekannter Charakter")

        while True:
            image_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                           if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif'))]

            for image_path in image_paths:
                if image_path in self.processed_files:
                    continue

                print(f"Verarbeite Datei: {image_path}")

                if image_path.lower().endswith(('.gif', '.webp')) and self.is_animated(image_path):
                    self.move_to_gifs_folder(image_path)
                    self.processed_files.add(image_path)
                    continue

                character_name, final_image_path = self.request(image_path)

                self.move_image(final_image_path, character_name or "Unbekannter Charakter")
                self.processed_files.add(final_image_path)

                print(f"Warte {self.rate_limit_time} Sekunden...")
                time.sleep(self.rate_limit_time)

            print("Warte auf neue Dateien...")
            time.sleep(10)

# Konfiguration
api_key = "652ac85e1fc1147b1d127ab68a557381dbb61910"
folder_path = "/home/imagesort/sort/NaoSort/ImagesToSort"
output_folder = "/home/imagesort/sort/NaoSort/SortedImages"
temp_folder = "/home/imagesort/sort/NaoSort/TempSorted"

os.makedirs(temp_folder, exist_ok=True)  # Temp-Ordner erstellen

sauce_nao = SauceNao(api_key, output_folder, temp_folder)
sauce_nao.process_images_from_folder(folder_path)
