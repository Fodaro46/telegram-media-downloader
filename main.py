import os
import asyncio
from telethon import TelegramClient
from dotenv import load_dotenv

# Caricamento variabili d ambiente
load_dotenv()

try:
    API_ID = int(os.getenv('API_ID'))
    API_HASH = os.getenv('API_HASH')
except (TypeError, ValueError):
    print("ERRORE: API_ID o API_HASH non configurati correttamente nel file .env")
    exit()

# Impostazioni predefinite
TARGET_CHANNEL = -1001078365372
BASE_PATH = './download'

async def main():
    # Inizializzazione client
    client = TelegramClient('session_personale', API_ID, API_HASH)
    
    print("--- CONFIGURAZIONE DOWNLOAD ---")
    parola_cercata = input("Inserisci la parola o l hashtag da cercare: ").strip()
    
    default_folder = parola_cercata.replace('#', '')
    input_cartella = input(f"Nome cartella di destinazione [Default: {default_folder}]: ").strip()
    
    folder_final = input_cartella if input_cartella else default_folder
    output_path = os.path.join(BASE_PATH, folder_final)

    # Autenticazione e avvio
    await client.start()
    print("Connessione stabilita con successo.")

    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f"Cartella creata: {output_path}")

    print(f"Ricerca di '{parola_cercata}' nel canale {TARGET_CHANNEL}...")
    
    count = 0
    # Scansione messaggi nel canale
    async for message in client.iter_messages(TARGET_CHANNEL, search=parola_cercata):
        if message.media:
            print(f"Scaricamento media ID: {message.id}...")
            path = await message.download_media(file=output_path)
            print(f"File salvato: {path}")
            count += 1

    if count == 0:
        print(f"Risultato: Nessun file trovato per '{parola_cercata}'.")
    else:
        print(f"Download terminato. Totale file scaricati: {count}")
        print(f"Percorso: {os.path.abspath(output_path)}")
    
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())