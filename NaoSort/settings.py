import os
import dotenv

def load_env(skip_prompts):
    if skip_prompts:
        if not dotenv.find_dotenv('.env'):
            print("Missing environment variables. Make sure that the .env file is set up correctly.")
            exit(1)
        else:
          dotenv.load_dotenv('.env')   # Loads the .env file, if it exists
          return
        
    # Check whether the .env file exists and whether the variables are empty
    dotenv.load_dotenv('.env')   # Loads the .env file, if it exists
    
    if not dotenv.find_dotenv('.env'):
        # .env-Datei existiert nicht, also erstellen
        with open(os.path.join(os.getcwd(), ".env"), "w") as file:
            pass  # Datei nur erstellen, nichts hinzufügen
        enter_settings()
    else:
        # Wenn alle Variablen vorhanden sind, frage den Benutzer, ob er die Einstellungen ändern möchte
        reenter = input("Do you want to reenter your settings? Y/N: ").strip().upper()
        if reenter == 'Y':
            enter_settings()
        elif reenter == 'N':
            pass
        else:
            print("Invalid input. Please enter 'Y' or 'N'.")
            load_env()  # Repeat the prompt if the input is invalid

def enter_settings():
    print('Enter your SauceNao API_Key:')
    api_key = input().strip()
    dotenv.set_key('.env', 'API_KEY', api_key)
    
    print('Enter the path to the folder containing the images you want to sort:')
    input_path = os.path.normpath(input().strip())
    dotenv.set_key('.env', 'INPUT_FOLDER', input_path)
    
    print('Enter the path to the folder where you want to move the sorted files:')
    output_path = os.path.normpath(input().strip())
    dotenv.set_key('.env', 'OUTPUT_PATH', output_path)
    dotenv.load_dotenv('.env')  # Load the .env
