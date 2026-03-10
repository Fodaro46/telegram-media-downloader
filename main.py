import os
import asyncio
from telethon import TelegramClient, events
from dotenv import load_dotenv

# 1. Caricamento credenziali
load_dotenv()
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')

# --- CONFIGURAZIONE UTENTE ---
HASHTAG = '#talia'           # La parola da cercare
BASE_PATH = './download'     # Dove vuoi salvare i file
FOLDER_NAME = 'Media_Talia'  # Nome della cartella finale
# -----------------------------

async def main():
    # Inizializza il client (creerà un file .session nella cartella)
    client = TelegramClient('session_personale', API_ID, API_HASH)
    
    await client.start()
    print("🚀 Bot avviato con successo!")

    # Crea il percorso completo
    output_path = os.path.join(BASE_PATH, FOLDER_NAME)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f"📂 Cartella creata: {output_path}")

    print(f"🔍 Ricerca di '{HASHTAG}' in corso...")
    
    # Cicla tra tutti i dialoghi per trovare il messaggio
    # Nota: puoi anche specificare l'ID del canale per velocizzare
    count = 0
    async for message in client.iter_messages(None, search=HASHTAG):
        if message.media:
            print(f"📥 Scaricando media dal messaggio ID: {message.id}...")
            # Scarica il file nella cartella specifica
            path = await message.download_media(file=output_path)
            print(f"✅ Salvato: {path}")
            count += 1

    print(f"\n✨ Operazione completata! Scaricati {count} elementi.")
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())