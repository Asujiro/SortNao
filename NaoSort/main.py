import os
import time
from sauce_nao import SauceNao  

def main():
    # Konfiguration
    api_key = ""
    folder_path = ""
    output_folder = ""
    temp_folder = ""

    # Create folder if not available
    os.makedirs(temp_folder, exist_ok=True)

    # Create and start SauceNao instance
    sauce_nao = SauceNao(api_key, output_folder, temp_folder)
    sauce_nao.process_images_from_folder(folder_path)

if __name__ == "__main__":
    main()