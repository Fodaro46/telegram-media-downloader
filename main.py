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

# Preset rapidi -> giorni a ritroso (None = tutto lo storico)
TEMPO_MAP = {
    "Ultimo mese": 30,
    "Ultimi 6 mesi": 182,
    "Ultimo anno": 365,
    "Ultimi due anni": 730,
    "Ultimi 3 anni": 1095,
    "Ultimi 4 anni": 1460,
    "Tutto": None,
}


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Telegram Student Downloader Pro")
        self.geometry("600x760")
        ctk.set_appearance_mode("dark")

        # Variabili di stato per il login
        self.client = None
        self.phone = None

        # UI
        self.label_title = ctk.CTkLabel(self, text="Telegram Downloader", font=("Roboto", 24, "bold"))
        self.label_title.pack(pady=20)

        self.entry_parola = ctk.CTkEntry(self, placeholder_text="Hashtag da cercare (es. #talia)", width=400)
        self.entry_parola.pack(pady=10)

        # --- Periodo: preset rapido ---
        self.combo_tempo = ctk.CTkComboBox(self, values=list(TEMPO_MAP.keys()), width=400)
        self.combo_tempo.set("Ultimo anno")
        self.combo_tempo.pack(pady=(10, 4))

        # --- Periodo: intervallo personalizzato (opzionale, ha la priorita') ---
        self.label_range = ctk.CTkLabel(
            self,
            text="Oppure intervallo preciso (opzionale, formato GG/MM/AAAA):",
            font=("Roboto", 11),
        )
        self.label_range.pack(pady=(6, 2))

        self.frame_range = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_range.pack(pady=2)
        self.entry_da = ctk.CTkEntry(self.frame_range, placeholder_text="Da  (GG/MM/AAAA)", width=195)
        self.entry_da.grid(row=0, column=0, padx=5)
        self.entry_a = ctk.CTkEntry(self.frame_range, placeholder_text="A  (GG/MM/AAAA)", width=195)
        self.entry_a.grid(row=0, column=1, padx=5)

        self.combo_tipo = ctk.CTkComboBox(self, values=["Documenti (PDF/DOC)", "Foto", "Video", "Tutto"], width=400)
        self.combo_tipo.set("Documenti (PDF/DOC)")
        self.combo_tipo.pack(pady=10)

        self.log_box = ctk.CTkTextbox(self, width=500, height=250)
        self.log_box.pack(pady=15)

        self.btn_start = ctk.CTkButton(self, text="AVVIA DOWNLOAD", command=self.start_thread, fg_color="#2b719e", font=("Roboto", 14, "bold"))
        self.btn_start.pack(pady=10)

    def log(self, text):
        # Tkinter non e' thread-safe: smista l'aggiornamento sul main thread.
        self.after(0, self._log_main, text)

    def _log_main(self, text):
        self.log_box.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] {text}\n")
        self.log_box.see("end")

    def _set_button_state(self, state):
        self.after(0, lambda: self.btn_start.configure(state=state))

    @staticmethod
    def _parse_data(testo):
        """Converte 'GG/MM/AAAA' in datetime naive. Lancia ValueError se invalida."""
        testo = testo.strip()
        if not testo:
            return None
        for sep in ("/", "-", "."):
            testo = testo.replace(sep, "/")
        return datetime.strptime(testo, "%d/%m/%Y")

    def _calcola_intervallo(self, da_raw, a_raw, preset):
        """Ritorna (data_da, data_a) naive. L'intervallo manuale ha priorita' sul preset."""
        data_da = self._parse_data(da_raw)
        data_a = self._parse_data(a_raw)

        if data_da or data_a:
            # Intervallo manuale: rendo 'A' inclusivo fino a fine giornata.
            if data_a:
                data_a = data_a + timedelta(days=1) - timedelta(seconds=1)
            if data_da and data_a and data_da > data_a:
                raise ValueError("La data 'Da' e' successiva alla data 'A'.")
            return data_da, data_a

        # Nessun intervallo manuale: uso il preset.
        giorni = TEMPO_MAP.get(preset)
        data_da = datetime.now() - timedelta(days=giorni) if giorni else None
        return data_da, None

    def start_thread(self):
        # Leggo i widget sul main thread e passo valori "puri" al worker.
        parola = self.entry_parola.get().strip()
        if not parola:
            self.log("ERRORE: Inserisci un hashtag!")
            return

        try:
            data_da, data_a = self._calcola_intervallo(
                self.entry_da.get(), self.entry_a.get(), self.combo_tempo.get()
            )
        except ValueError as e:
            self.log(f"ERRORE data: {e} (usa il formato GG/MM/AAAA)")
            return

        tipo_f = self.combo_tipo.get()

        self.btn_start.configure(state="disabled")
        threading.Thread(
            target=lambda: asyncio.run(self.run_logic(parola, data_da, data_a, tipo_f)),
            daemon=True,
        ).start()

    # Funzione per chiedere dati alla GUI dal thread di Telegram
    async def get_input_gui(self, prompt):
        dialog = ctk.CTkInputDialog(text=prompt, title="Accesso Telegram")
        return dialog.get_input()

    async def run_logic(self, parola, data_da, data_a, tipo_f):
        try:
            if not API_ID or not API_HASH:
                self.log("ERRORE: API_ID/API_HASH mancanti. Controlla il file .env")
                return

            if data_da or data_a:
                da_txt = data_da.strftime('%d/%m/%Y') if data_da else "inizio"
                a_txt = data_a.strftime('%d/%m/%Y') if data_a else "oggi"
                self.log(f"Periodo: da {da_txt} a {a_txt}")

            # Avvio Client con gestione interattiva del login
            self.client = TelegramClient('session_personale', int(API_ID), API_HASH)

            await self.client.connect()

            if not await self.client.is_user_authorized():
                self.log("Richiesta autorizzazione...")
                phone = await self.get_input_gui("Inserisci il tuo numero (es. +39347...)")
                if not phone:
                    return

                await self.client.send_code_request(phone)
                code = await self.get_input_gui("Inserisci il codice ricevuto su Telegram:")

                try:
                    await self.client.sign_in(phone, code)
                except errors.SessionPasswordNeededError:
                    pw = await self.get_input_gui("Inserisci la Password 2FA:")
                    await self.client.sign_in(password=pw)

            self.log("Login effettuato!")

            folder = os.path.join('./download', parola.replace('#', ''))
            os.makedirs(folder, exist_ok=True)

            count = 0
            # iter_messages restituisce i messaggi dal piu' recente al piu' vecchio.
            async for message in self.client.iter_messages(TARGET_CHANNEL, search=parola):
                msg_date = message.date.replace(tzinfo=None)

                # Troppo vecchio: essendo ordinati, posso fermarmi del tutto.
                if data_da and msg_date < data_da:
                    break
                # Troppo recente rispetto all'estremo superiore: salto.
                if data_a and msg_date > data_a:
                    continue

                scarica = False
                if message.media:
                    if "Documenti" in tipo_f and message.document:
                        scarica = True
                    elif "Foto" in tipo_f and message.photo:
                        scarica = True
                    elif "Video" in tipo_f and message.video:
                        scarica = True
                    elif "Tutto" in tipo_f:
                        scarica = True

                if scarica:
                    self.log(f"Scaricando messaggio {message.id}...")
                    await message.download_media(file=folder)
                    count += 1

            self.log(f"FINE! Scaricati {count} file.")

        except Exception as e:
            self.log(f"ERRORE CRITICO: {str(e)}")
        finally:
            if self.client:
                await self.client.disconnect()
            self._set_button_state("normal")


if __name__ == "__main__":
    app = App()
    app.mainloop()
