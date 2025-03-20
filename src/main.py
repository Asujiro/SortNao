import argparse
import os
from sauce_nao import SauceNao
import settings

def main():

    parser = argparse.ArgumentParser(description="Process input prompts.")
    parser.add_argument('--SkipPrompts', action='store_true', help="Skip the input prompts.")
    args = parser.parse_args()

    settings.load_env(args.SkipPrompts)

    # Konfiguration
    api_key = os.getenv("API_KEY")
    folder_path = os.getenv("INPUT_FOLDER")
    output_folder = os.getenv("OUTPUT_PATH")
    simularity = float(os.getenv("SIMULARITY", "50.0"))

    if not api_key or not folder_path or not output_folder:
        print("Missing environment variables. Make sure that the .env file is set up correctly.")
        return

    # Erstelle und starte die SauceNao-Instanz
    sauce_nao = SauceNao(api_key, output_folder, simularity)
    sauce_nao.process_images_from_folder(folder_path)

if __name__ == "__main__":
    main()