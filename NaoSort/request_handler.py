import requests
import time
import shutil
import os
from image_utils import convert_to_png

class SauceNaoRequest:
    def __init__(self, api_key, endpoint="https://saucenao.com/search.php"):
        self.api_key = api_key
        self.endpoint = endpoint

    def request(self, image_path):
        image_path = convert_to_png(image_path) or image_path

        try:
            with open(image_path, 'rb') as file:
                files = {'file': ('file.png', file, 'image/png')}
                data = {'api_key': self.api_key, 'output_type': '2', 'db': '9', 'numres': '16'}

                response = requests.post(self.endpoint, files=files, data=data)

                if response.status_code == 200:
                    return response.json(), image_path
                elif response.status_code == 429:
                    print("Rate Limit erreicht! Warte 24 Stunden...")
                    time.sleep(86400)
                    return self.request(image_path)
                else:
                    print(f"Fehler beim Abrufen der Daten: {response.status_code}")
                    return None, image_path
        except Exception as e:
            print(f"Fehler bei der Anfrage: {e}")
            return None, image_path
