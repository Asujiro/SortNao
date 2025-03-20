import os
import re
import time
import shutil
from image_utils import is_animated, move_to_gifs_folder
from request_handler import SauceNaoRequest

class SauceNao:
    def __init__(self, api_key, output_folder, simularity):
        self.api_key = api_key
        self.output_folder = output_folder
        self.rate_limit_time = 30
        self.processed_files = set()
        self.request_handler = SauceNaoRequest(api_key)
        self.counter = 0
        self.shutdown_Counter = 0
        self.similarity = simularity
    
    # Clean the folder name from special characters
    def clean_folder_name(self, name):
        cleaned_name = re.sub(r'[\\/:*?"<>|()]', '', name)
        cleaned_name = cleaned_name.replace(" ", "_")
        cleaned_name = re.sub(r'_{2,}', '_', cleaned_name)
        return cleaned_name.rstrip('_')

    # Move the image to the target folder
    def move_image(self, image_path, character_name):
        folder_name = "unknown" if character_name == "Unknown character" else self.clean_folder_name(character_name)
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
        print(f"Image moved to: {target_path}")

    # Process the images from the input folder
    def process_images_from_folder(self, folder_path):
        while True:
            image_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                           if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif'))]

            for image_path in image_paths:
                if image_path in self.processed_files:
                    continue

                print(f"Process file: {image_path}")

                if image_path.lower().endswith(('.gif', '.webp')) and is_animated(image_path):
                    move_to_gifs_folder(image_path, self.output_folder)
                    self.processed_files.add(image_path)
                    continue

                response, final_image_path = self.request_handler.request(image_path)
                character_name = self.parse_response(response) if response else "Unknown character"
                self.move_image(final_image_path, character_name)

                self.processed_files.add(final_image_path)

                self.counter += 1
                if self.counter == 4:
                    print(f"Wait {self.rate_limit_time} seconds...")
                    self.counter = 0
                    time.sleep(self.rate_limit_time)

            print("Wait for new files...")
            self.shutdown_Counter += 1
            if self.shutdown_Counter == 5:
                print("No new files found. Exiting program...")
                exit(0)
            time.sleep(30)

    # Parse the response from the API
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
            print(f"Recognized character: {best_character} ({highest_similarity}%)")
            return best_character
        else:
            print("Nothing recognized - image is sorted as 'unknown'.")
            return "Unknown character"
