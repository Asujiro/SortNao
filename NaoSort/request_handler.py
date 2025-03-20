import requests
import shutil
import os
from image_utils import convert_to_png

class SauceNaoRequest:
    def __init__(self, api_key, endpoint="https://saucenao.com/search.php"):
        self.api_key = api_key
        self.endpoint = endpoint

    # Request the data from the SauceNao API
    def request(self, image_path):
        original_image_path = image_path
        image_path = convert_to_png(image_path) or image_path

        try:
            with open(image_path, 'rb') as file:
                files = {'file': ('file.png', file, 'image/png')}
                data = {'api_key': self.api_key, 'output_type': '2', 'db': '9', 'numres': '16'}

                response = requests.post(self.endpoint, files=files, data=data)

                if response.status_code == 200:
                    return response.json(), image_path
                elif response.status_code == 429:
                    self.handle_rate_limit(image_path, original_image_path)
                else:
                    print(f"Error when retrieving the data: {response.status_code}")
                    return None, image_path
        except Exception as e:
            print(f"Error in the request: {e}")
            return None, image_path
        
    # Handle the rate limit of the API request and save the file before exiting
    def handle_rate_limit(self, image_path, original_image_path):
        print("Rate limit reached! saving currend file...")

        # Here we save the PNG file in the input folder
        input_folder = os.path.dirname(original_image_path)
        temp_path = os.path.join(input_folder, os.path.basename(image_path))
        shutil.move(image_path, temp_path)  # Converted PNG is moved
        print(f"Image cached: {temp_path}")

        print("Rate limit reached! Exiting program...")
        # Close the program after saving the file and reching the rate limit
        exit(0)