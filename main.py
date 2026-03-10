import os
import asyncio
import threading
from datetime import datetime, timedelta
import customtkinter as ctk
from telethon import TelegramClient, errors
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURAZIONE ---
TARGET_CHANNEL = -1001078365372  
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Telegram Student Downloader Pro")
        self.geometry("600x650")
        ctk.set_appearance_mode("dark")

        # Variabili di stato per il login
        self.client = None
        self.phone = None
        
        # UI
        self.label_title = ctk.CTkLabel(self, text="Telegram Downloader", font=("Roboto", 24, "bold"))
        self.label_title.pack(pady=20)

        self.entry_parola = ctk.CTkEntry(self, placeholder_text="Hashtag da cercare (es. #talia)", width=400)
        self.entry_parola.pack(pady=10)

        self.combo_tempo = ctk.CTkComboBox(self, values=["Ultimo mese", "Ultimi 6 mesi", "Ultimo anno","Ultimi due anni","Ultimi 3 anni", "Ultimi 4 anni", "Tutto"], width=400)
        self.combo_tempo.set("Ultimo anno")
        self.combo_tempo.pack(pady=10)

        self.combo_tipo = ctk.CTkComboBox(self, values=["Documenti (PDF/DOC)", "Foto", "Video", "Tutto"], width=400)
        self.combo_tipo.set("Documenti (PDF/DOC)")
        self.combo_tipo.pack(pady=10)

        self.log_box = ctk.CTkTextbox(self, width=500, height=250)
        self.log_box.pack(pady=15)

        self.btn_start = ctk.CTkButton(self, text="AVVIA DOWNLOAD", command=self.start_thread, fg_color="#2b719e", font=("Roboto", 14, "bold"))
        self.btn_start.pack(pady=10)

    def log(self, text):
        self.log_box.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] {text}\n")
        self.log_box.see("end")

    def start_thread(self):
        self.btn_start.configure(state="disabled")
        threading.Thread(target=lambda: asyncio.run(self.run_logic()), daemon=True).start()

    # Funzione per chiedere dati alla GUI dal thread di Telegram
    async def get_input_gui(self, prompt):
        dialog = ctk.CTkInputDialog(text=prompt, title="Accesso Telegram")
        return dialog.get_input()

    async def run_logic(self):
        try:
            parola = self.entry_parola.get().strip()
            if not parola:
                self.log("ERRORE: Inserisci un hashtag!")
                self.btn_start.configure(state="normal")
                return

            # Configurazione filtri
            tempo_map = {"Ultimo mese": 30, "Ultimi 6 mesi": 182, "Ultimo anno": 365,"Ultimi due anni": 730 ,"Ultimi 3 anni": 1095, "Ultimi 4 anni": 1460 , "Tutto": None}
            giorni = tempo_map.get(self.combo_tempo.get())
            data_limite = datetime.now() - timedelta(days=giorni) if giorni else None
            tipo_f = self.combo_tipo.get()

            # Avvio Client con gestione interattiva del login
            self.client = TelegramClient('session_personale', int(API_ID), API_HASH)
            
            await self.client.connect()

            if not await self.client.is_user_authorized():
                self.log("Richiesta autorizzazione...")
                phone = await self.get_input_gui("Inserisci il tuo numero (es. +39347...)")
                if not phone: return
                
                await self.client.send_code_request(phone)
                code = await self.get_input_gui("Inserisci il codice ricevuto su Telegram:")
                
                try:
                    await self.client.sign_in(phone, code)
                except errors.SessionPasswordNeededError:
                    pw = await self.get_input_gui("Inserisci la Password 2FA:")
                    await self.client.sign_in(password=pw)

            self.log("Login effettuato!")
            
            folder = os.path.join('./download', parola.replace('#',''))
            os.makedirs(folder, exist_ok=True)

            count = 0
            async for message in self.client.iter_messages(TARGET_CHANNEL, search=parola):
                if data_limite and message.date.replace(tzinfo=None) < data_limite:
                    continue

                scarica = False
                if message.media:
                    if "Documenti" in tipo_f and message.document: scarica = True
                    elif "Foto" in tipo_f and message.photo: scarica = True
                    elif "Video" in tipo_f and message.video: scarica = True
                    elif "Tutto" in tipo_f: scarica = True

                if scarica:
                    self.log(f"Scaricando messaggio {message.id}...")
                    await message.download_media(file=folder)
                    count += 1

            self.log(f"FINE! Scaricati {count} file.")
            
        except Exception as e:
            self.log(f"ERRORE CRITICO: {str(e)}")
        finally:
            await self.client.disconnect()
            self.btn_start.configure(state="normal")

if __name__ == "__main__":
    app = App()
    app.mainloop()