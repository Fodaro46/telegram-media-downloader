import os
import re
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

# Categorie selezionabili (etichetta -> attiva di default)
CATEGORIE = {
    "Documenti": True,
    "Foto": False,
    "Video": False,
    "Audio": False,
    "Vocali": False,
    "Archivi": False,
    "GIF": False,
}

ARCHIVE_EXTS = {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"}
INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Telegram Student Downloader Pro")
        self.geometry("680x880")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Stato
        self.client = None
        self.stop_event = threading.Event()
        self.last_folder = None
        self.tipo_checks = {}

        # ---------- HEADER ----------
        header = ctk.CTkFrame(self, fg_color="#1f2d3d", corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(
            header, text="📥  Telegram Downloader", font=("Segoe UI", 26, "bold")
        ).pack(pady=18)

        # contenitore principale
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=12)

        # ---------- HASHTAG ----------
        self._sezione(body, "🔍  Hashtag da cercare")
        self.entry_parola = ctk.CTkEntry(body, placeholder_text="es. #sisop", height=36)
        self.entry_parola.pack(fill="x", pady=(0, 14))

        # ---------- PERIODO ----------
        self._sezione(body, "📅  Periodo")
        self.combo_tempo = ctk.CTkComboBox(body, values=list(TEMPO_MAP.keys()), height=36)
        self.combo_tempo.set("Ultimo anno")
        self.combo_tempo.pack(fill="x")
        ctk.CTkLabel(
            body, text="Oppure intervallo preciso (opzionale, GG/MM/AAAA):",
            font=("Segoe UI", 11), text_color="#9aa6b2",
        ).pack(anchor="w", pady=(8, 2))
        frame_range = ctk.CTkFrame(body, fg_color="transparent")
        frame_range.pack(fill="x", pady=(0, 14))
        self.entry_da = ctk.CTkEntry(frame_range, placeholder_text="Da  (GG/MM/AAAA)", height=34)
        self.entry_da.pack(side="left", expand=True, fill="x", padx=(0, 6))
        self.entry_a = ctk.CTkEntry(frame_range, placeholder_text="A  (GG/MM/AAAA)", height=34)
        self.entry_a.pack(side="left", expand=True, fill="x", padx=(6, 0))

        # ---------- TIPI FILE ----------
        self._sezione(body, "📁  Tipi di file (selezione multipla)")
        grid = ctk.CTkFrame(body, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 6))
        for i, (nome, attivo) in enumerate(CATEGORIE.items()):
            cb = ctk.CTkCheckBox(grid, text=nome)
            if attivo:
                cb.select()
            cb.grid(row=i // 4, column=i % 4, sticky="w", padx=8, pady=4)
            self.tipo_checks[nome] = cb

        # ---------- ESTENSIONI ----------
        ctk.CTkLabel(
            body, text="Filtra per estensione (opzionale, es. pdf, docx, zip):",
            font=("Segoe UI", 11), text_color="#9aa6b2",
        ).pack(anchor="w", pady=(8, 2))
        self.entry_ext = ctk.CTkEntry(body, placeholder_text="lascia vuoto per tutte", height=34)
        self.entry_ext.pack(fill="x", pady=(0, 14))

        # ---------- PROGRESSO ----------
        self.progress = ctk.CTkProgressBar(body, height=14)
        self.progress.set(0)
        self.progress.pack(fill="x", pady=(2, 4))
        self.status = ctk.CTkLabel(body, text="Pronto.", font=("Segoe UI", 11), text_color="#9aa6b2")
        self.status.pack(anchor="w")

        # ---------- LOG ----------
        self.log_box = ctk.CTkTextbox(body, height=200, font=("Consolas", 11))
        self.log_box.pack(fill="both", expand=True, pady=10)

        # ---------- PULSANTI ----------
        btns = ctk.CTkFrame(body, fg_color="transparent")
        btns.pack(fill="x", pady=(0, 6))
        self.btn_start = ctk.CTkButton(
            btns, text="▶  AVVIA DOWNLOAD", command=self.start_thread,
            height=42, font=("Segoe UI", 14, "bold"),
        )
        self.btn_start.pack(side="left", expand=True, fill="x", padx=(0, 6))
        self.btn_folder = ctk.CTkButton(
            btns, text="📂 Apri cartella", command=self.apri_cartella,
            height=42, width=150, fg_color="#3a4a5a", hover_color="#4a5d6e",
        )
        self.btn_folder.pack(side="left")

    # ---------------- HELPER UI ----------------
    def _sezione(self, parent, testo):
        ctk.CTkLabel(parent, text=testo, font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(4, 4))

    def log(self, text):
        self.after(0, self._log_main, text)

    def _log_main(self, text):
        self.log_box.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] {text}\n")
        self.log_box.see("end")

    def _set_status(self, text):
        self.after(0, lambda: self.status.configure(text=text))

    def _set_progress(self, val):
        self.after(0, lambda: self.progress.set(val))

    def apri_cartella(self):
        if self.last_folder and os.path.isdir(self.last_folder):
            try:
                os.startfile(os.path.abspath(self.last_folder))
            except Exception as e:
                self.log(f"Impossibile aprire la cartella: {e}")
        else:
            self.log("Nessuna cartella di download ancora disponibile.")

    # ---------------- PARSING DATE ----------------
    @staticmethod
    def _parse_data(testo):
        testo = testo.strip()
        if not testo:
            return None
        for sep in ("-", "."):
            testo = testo.replace(sep, "/")
        return datetime.strptime(testo, "%d/%m/%Y")

    def _calcola_intervallo(self, da_raw, a_raw, preset):
        data_da = self._parse_data(da_raw)
        data_a = self._parse_data(a_raw)
        if data_da or data_a:
            if data_a:
                data_a = data_a + timedelta(days=1) - timedelta(seconds=1)
            if data_da and data_a and data_da > data_a:
                raise ValueError("La data 'Da' e' successiva alla data 'A'.")
            return data_da, data_a
        giorni = TEMPO_MAP.get(preset)
        data_da = datetime.now() - timedelta(days=giorni) if giorni else None
        return data_da, None

    # ---------------- CLASSIFICAZIONE MEDIA ----------------
    @staticmethod
    def _categoria(message):
        if not message.media:
            return None
        if message.photo:
            return "Foto"
        if message.voice:
            return "Vocali"
        if message.gif:
            return "GIF"
        if getattr(message, "video_note", None) or message.video:
            return "Video"
        if message.audio:
            return "Audio"
        if message.document:
            ext = (message.file.ext or "").lower() if message.file else ""
            return "Archivi" if ext in ARCHIVE_EXTS else "Documenti"
        return None

    def _da_scaricare(self, message, tipi_sel, exts):
        cat = self._categoria(message)
        if cat is None or cat not in tipi_sel:
            return False
        if exts:
            ext = (message.file.ext or "").lower().lstrip(".") if message.file else ""
            if ext not in exts:
                return False
        return True

    @staticmethod
    def _percorso_file(folder, message):
        name = message.file.name if (message.file and message.file.name) else None
        ext = (message.file.ext if message.file else "") or ""
        base = name if name else f"file{ext}"
        base = INVALID_CHARS.sub("_", base)
        return os.path.join(folder, f"{message.id}_{base}")

    async def _album_fratelli(self, message):
        ids = list(range(message.id - 9, message.id + 10))
        try:
            fratelli = await self.client.get_messages(TARGET_CHANNEL, ids=ids)
        except Exception:
            return [message]
        return [m for m in fratelli if m and m.grouped_id == message.grouped_id]

    # ---------------- AVVIO / STOP ----------------
    def start_thread(self):
        parola = self.entry_parola.get().strip()
        if not parola:
            self.log("ERRORE: Inserisci un hashtag!")
            return

        tipi_sel = {n for n, cb in self.tipo_checks.items() if cb.get()}
        if not tipi_sel:
            self.log("ERRORE: Seleziona almeno un tipo di file!")
            return

        try:
            data_da, data_a = self._calcola_intervallo(
                self.entry_da.get(), self.entry_a.get(), self.combo_tempo.get()
            )
        except ValueError as e:
            self.log(f"ERRORE data: {e} (usa il formato GG/MM/AAAA)")
            return

        exts = {
            e.strip().lstrip(".").lower()
            for e in re.split(r"[,\s]+", self.entry_ext.get())
            if e.strip()
        }

        self.stop_event.clear()
        self.progress.set(0)
        self.btn_start.configure(text="⛔  FERMA", fg_color="#9e2b2b",
                                 hover_color="#7e2222", command=self.request_stop)
        threading.Thread(
            target=lambda: asyncio.run(self.run_logic(parola, data_da, data_a, tipi_sel, exts)),
            daemon=True,
        ).start()

    def request_stop(self):
        self.stop_event.set()
        self.log("Interruzione richiesta, attendo il file corrente...")

    def _fine_run(self):
        self.btn_start.configure(text="▶  AVVIA DOWNLOAD", fg_color=["#3a7ebf", "#1f538d"],
                                 hover_color=["#325882", "#14375e"], command=self.start_thread)

    async def get_input_gui(self, prompt):
        dialog = ctk.CTkInputDialog(text=prompt, title="Accesso Telegram")
        return dialog.get_input()

    # ---------------- LOGICA PRINCIPALE ----------------
    async def run_logic(self, parola, data_da, data_a, tipi_sel, exts):
        try:
            if not API_ID or not API_HASH:
                self.log("ERRORE: API_ID/API_HASH mancanti. Controlla il file .env")
                return

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
            self.last_folder = folder

            # ---- Fase 1: raccolta candidati (con espansione album) ----
            self.log("Ricerca messaggi in corso...")
            self._set_status("Ricerca in corso...")
            candidati = {}
            gruppi_visti = set()

            async for message in self.client.iter_messages(TARGET_CHANNEL, search=parola):
                if self.stop_event.is_set():
                    break
                msg_date = message.date.replace(tzinfo=None)
                if data_da and msg_date < data_da:
                    break
                if data_a and msg_date > data_a:
                    continue

                if message.grouped_id and message.grouped_id not in gruppi_visti:
                    # Album: recupero tutti gli elementi, anche quelli senza hashtag.
                    gruppi_visti.add(message.grouped_id)
                    for fratello in await self._album_fratelli(message):
                        if self._da_scaricare(fratello, tipi_sel, exts):
                            candidati[fratello.id] = fratello
                elif self._da_scaricare(message, tipi_sel, exts):
                    candidati[message.id] = message

            messaggi = list(candidati.values())
            totale = len(messaggi)
            self.log(f"Trovati {totale} file corrispondenti.")

            # ---- Fase 2: download ----
            count = saltati = 0
            for i, message in enumerate(messaggi, 1):
                if self.stop_event.is_set():
                    self.log("⛔ Interrotto dall'utente.")
                    break
                path = self._percorso_file(folder, message)
                if os.path.exists(path):
                    saltati += 1
                else:
                    self._set_status(f"Scaricamento {i}/{totale}...")
                    await message.download_media(file=path)
                    count += 1
                    self.log(f"[{i}/{totale}] {os.path.basename(path)}")
                self._set_progress(i / totale if totale else 1)

            fine = f"✅ FINE! Scaricati {count} file"
            if saltati:
                fine += f" ({saltati} già presenti, saltati)"
            self.log(fine + ".")
            self._set_status(fine)

        except Exception as e:
            self.log(f"ERRORE CRITICO: {str(e)}")
            self._set_status("Errore.")
        finally:
            if self.client:
                await self.client.disconnect()
            self.after(0, self._fine_run)


if __name__ == "__main__":
    app = App()
    app.mainloop()
