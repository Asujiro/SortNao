import os
import time
from sauce_nao import SauceNao  

def main():
    # Konfiguration
    api_key = "652ac85e1fc1147b1d127ab68a557381dbb61910"
    folder_path = "/home/imagesort/sort/NaoSort/ImagesToSort"
    output_folder = "/home/imagesort/sort/NaoSort/SortedImages"
    temp_folder = "/home/imagesort/sort/NaoSort/TempSorted"

    # Ordner erstellen, falls nicht vorhanden
    os.makedirs(temp_folder, exist_ok=True)

    # SauceNao-Instanz erstellen und starten
    sauce_nao = SauceNao(api_key, output_folder, temp_folder)
    sauce_nao.process_images_from_folder(folder_path)

if __name__ == "__main__":
    main()