import os
import re
import json
import asyncio
import threading
from datetime import datetime, timedelta
import customtkinter as ctk
from telethon import TelegramClient, errors
from telethon.tl.functions.messages import CheckChatInviteRequest, ImportChatInviteRequest
from telethon.tl.types import ChatInviteAlready
from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = "config.json"

# Quick presets -> days to go back (None = entire history)
TEMPO_MAP = {
    "Ultimo mese": 30,
    "Ultimi 6 mesi": 182,
    "Ultimo anno": 365,
    "Ultimi due anni": 730,
    "Ultimi 3 anni": 1095,
    "Ultimi 4 anni": 1460,
    "Tutto": None,
}

# Selectable categories (label -> enabled by default)
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
        self.geometry("700x900")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # State
        self.client = None
        self.entity = None
        self.stop_event = threading.Event()
        self.last_folder = None
        self.tipo_checks = {}

        cfg = self._load_config()

        # ---------- HEADER ----------
        header = ctk.CTkFrame(self, fg_color="#1f2d3d", corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(
            header, text="📥  Telegram Downloader", font=("Segoe UI", 26, "bold")
        ).pack(pady=16)

        # ---------- TABS ----------
        self.tabs = ctk.CTkTabview(self, fg_color="transparent")
        self.tabs.pack(fill="both", expand=True, padx=20, pady=(4, 10))
        tab_cfg = self.tabs.add("⚙️ Configurazione")
        tab_dl = self.tabs.add("⬇️ Download")

        self._build_tab_config(tab_cfg, cfg)
        self._build_tab_download(tab_dl)

        # If the configuration is incomplete, start on the Configuration tab
        if not (cfg.get("api_id") and cfg.get("api_hash") and cfg.get("channel")):
            self.tabs.set("⚙️ Configurazione")
        else:
            self.tabs.set("⬇️ Download")

    # ================= CONFIGURATION TAB =================
    def _build_tab_config(self, tab, cfg):
        banner = ctk.CTkFrame(tab, fg_color="#243447", corner_radius=10)
        banner.pack(fill="x", pady=(6, 14))
        istruzioni = (
            "ℹ️  Come configurare:\n"
            "1.  Vai su my.telegram.org → 'API development tools' e copia API ID e API Hash.\n"
            "2.  Incolla qui sotto le credenziali (restano solo sul tuo PC, in config.json).\n"
            "3.  Nel campo Canale incolla il link d'invito (t.me/+...), lo @username\n"
            "     oppure l'ID numerico del canale. Se è un link d'invito, il bot ci entra da solo.\n"
            "4.  Premi 'Salva configurazione', poi passa alla scheda Download."
        )
        ctk.CTkLabel(banner, text=istruzioni, justify="left", font=("Segoe UI", 12),
                     text_color="#cdd6df").pack(anchor="w", padx=14, pady=12)

        self._sezione(tab, "🔑  API ID")
        self.entry_api_id = ctk.CTkEntry(tab, placeholder_text="es. 1234567", height=36)
        self.entry_api_id.pack(fill="x", pady=(0, 12))
        self.entry_api_id.insert(0, cfg.get("api_id", ""))

        self._sezione(tab, "🔑  API Hash")
        self.entry_api_hash = ctk.CTkEntry(tab, placeholder_text="es. a1b2c3d4e5f6...", height=36)
        self.entry_api_hash.pack(fill="x", pady=(0, 12))
        self.entry_api_hash.insert(0, cfg.get("api_hash", ""))

        self._sezione(tab, "📡  Canale (link invito / @username / ID)")
        self.entry_channel = ctk.CTkEntry(
            tab, placeholder_text="es. https://t.me/+AbCdEf  oppure  @nomecanale  oppure  -100123...",
            height=36)
        self.entry_channel.pack(fill="x", pady=(0, 16))
        self.entry_channel.insert(0, cfg.get("channel", ""))

        ctk.CTkButton(tab, text="💾  Salva configurazione", height=42,
                      font=("Segoe UI", 14, "bold"), command=self.salva_config).pack(fill="x")
        self.lbl_cfg_status = ctk.CTkLabel(tab, text="", font=("Segoe UI", 11),
                                           text_color="#7fd18a")
        self.lbl_cfg_status.pack(anchor="w", pady=6)

    # ================= DOWNLOAD TAB =================
    def _build_tab_download(self, tab):
        self._sezione(tab, "🔍  Hashtag da cercare")
        self.entry_parola = ctk.CTkEntry(tab, placeholder_text="es. #sisop", height=36)
        self.entry_parola.pack(fill="x", pady=(0, 12))

        self._sezione(tab, "📅  Periodo")
        self.combo_tempo = ctk.CTkComboBox(tab, values=list(TEMPO_MAP.keys()), height=36)
        self.combo_tempo.set("Ultimo anno")
        self.combo_tempo.pack(fill="x")
        ctk.CTkLabel(tab, text="Oppure intervallo preciso (opzionale, GG/MM/AAAA):",
                     font=("Segoe UI", 11), text_color="#9aa6b2").pack(anchor="w", pady=(8, 2))
        frame_range = ctk.CTkFrame(tab, fg_color="transparent")
        frame_range.pack(fill="x", pady=(0, 12))
        self.entry_da = ctk.CTkEntry(frame_range, placeholder_text="Da  (GG/MM/AAAA)", height=34)
        self.entry_da.pack(side="left", expand=True, fill="x", padx=(0, 6))
        self.entry_a = ctk.CTkEntry(frame_range, placeholder_text="A  (GG/MM/AAAA)", height=34)
        self.entry_a.pack(side="left", expand=True, fill="x", padx=(6, 0))

        self._sezione(tab, "📁  Tipi di file (selezione multipla)")
        grid = ctk.CTkFrame(tab, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 4))
        for i, (nome, attivo) in enumerate(CATEGORIE.items()):
            cb = ctk.CTkCheckBox(grid, text=nome)
            if attivo:
                cb.select()
            cb.grid(row=i // 4, column=i % 4, sticky="w", padx=8, pady=4)
            self.tipo_checks[nome] = cb

        ctk.CTkLabel(tab, text="Filtra per estensione (opzionale, es. pdf, docx, zip):",
                     font=("Segoe UI", 11), text_color="#9aa6b2").pack(anchor="w", pady=(8, 2))
        self.entry_ext = ctk.CTkEntry(tab, placeholder_text="lascia vuoto per tutte", height=34)
        self.entry_ext.pack(fill="x", pady=(0, 12))

        self.progress = ctk.CTkProgressBar(tab, height=14)
        self.progress.set(0)
        self.progress.pack(fill="x", pady=(2, 4))
        self.status = ctk.CTkLabel(tab, text="Pronto.", font=("Segoe UI", 11), text_color="#9aa6b2")
        self.status.pack(anchor="w")

        self.log_box = ctk.CTkTextbox(tab, height=170, font=("Consolas", 11))
        self.log_box.pack(fill="both", expand=True, pady=8)

        btns = ctk.CTkFrame(tab, fg_color="transparent")
        btns.pack(fill="x", pady=(0, 4))
        self.btn_start = ctk.CTkButton(btns, text="▶  AVVIA DOWNLOAD", command=self.start_thread,
                                       height=42, font=("Segoe UI", 14, "bold"))
        self.btn_start.pack(side="left", expand=True, fill="x", padx=(0, 6))
        self.btn_folder = ctk.CTkButton(btns, text="📂 Apri cartella", command=self.apri_cartella,
                                        height=42, width=150, fg_color="#3a4a5a",
                                        hover_color="#4a5d6e")
        self.btn_folder.pack(side="left")

    # ---------------- CONFIG ----------------
    @staticmethod
    def _load_config():
        cfg = {}
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
            except Exception:
                cfg = {}
        # Fall back to .env for credentials (backward compatibility)
        cfg.setdefault("api_id", os.getenv("API_ID", "") or "")
        cfg.setdefault("api_hash", os.getenv("API_HASH", "") or "")
        cfg.setdefault("channel", "")
        return cfg

    def salva_config(self):
        data = {
            "api_id": self.entry_api_id.get().strip(),
            "api_hash": self.entry_api_hash.get().strip(),
            "channel": self.entry_channel.get().strip(),
        }
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self.lbl_cfg_status.configure(text="✅ Configurazione salvata in config.json",
                                          text_color="#7fd18a")
        except Exception as e:
            self.lbl_cfg_status.configure(text=f"❌ Errore nel salvataggio: {e}",
                                          text_color="#e08585")

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

    # ---------------- CHANNEL RESOLUTION ----------------
    async def _risolvi_canale(self, raw):
        raw = raw.strip()
        if not raw:
            raise ValueError("Inserisci il canale nella scheda Configurazione.")

        # Private invite link: t.me/+hash  or  t.me/joinchat/hash
        m = re.search(r't\.me/(?:joinchat/|\+)([\w-]+)', raw)
        if m:
            invite = m.group(1)
            res = await self.client(CheckChatInviteRequest(invite))
            if isinstance(res, ChatInviteAlready):
                return res.chat
            updates = await self.client(ImportChatInviteRequest(invite))
            return updates.chats[0]

        # Numeric ID
        if re.fullmatch(r'-?\d+', raw):
            return await self.client.get_entity(int(raw))

        # @username or public link t.me/channelname
        return await self.client.get_entity(raw)

    # ---------------- MEDIA CLASSIFICATION ----------------
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
            fratelli = await self.client.get_messages(self.entity, ids=ids)
        except Exception:
            return [message]
        return [m for m in fratelli if m and m.grouped_id == message.grouped_id]

    # ---------------- START / STOP ----------------
    def start_thread(self):
        api_id = self.entry_api_id.get().strip()
        api_hash = self.entry_api_hash.get().strip()
        channel = self.entry_channel.get().strip()
        if not (api_id and api_hash and channel):
            self.log("ERRORE: completa API ID, API Hash e Canale nella scheda Configurazione.")
            self.tabs.set("⚙️ Configurazione")
            return
        if not api_id.isdigit():
            self.log("ERRORE: l'API ID deve essere numerico.")
            self.tabs.set("⚙️ Configurazione")
            return

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
                self.entry_da.get(), self.entry_a.get(), self.combo_tempo.get())
        except ValueError as e:
            self.log(f"ERRORE data: {e} (usa il formato GG/MM/AAAA)")
            return

        exts = {e.strip().lstrip(".").lower()
                for e in re.split(r"[,\s]+", self.entry_ext.get()) if e.strip()}

        # Save the config so it doesn't need to be re-entered next time.
        self.salva_config()

        self.stop_event.clear()
        self.progress.set(0)
        self.btn_start.configure(text="⛔  FERMA", fg_color="#9e2b2b",
                                 hover_color="#7e2222", command=self.request_stop)
        threading.Thread(
            target=lambda: asyncio.run(
                self.run_logic(int(api_id), api_hash, channel, parola, data_da, data_a, tipi_sel, exts)),
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

    # ---------------- MAIN LOGIC ----------------
    async def run_logic(self, api_id, api_hash, channel, parola, data_da, data_a, tipi_sel, exts):
        try:
            self.client = TelegramClient('session_personale', api_id, api_hash)
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

            # Resolve the channel
            try:
                self.entity = await self._risolvi_canale(channel)
                nome = getattr(self.entity, "title", None) or getattr(self.entity, "username", channel)
                self.log(f"Canale: {nome}")
            except Exception as e:
                self.log(f"ERRORE canale: impossibile risolvere '{channel}' ({e}). "
                         f"Prova con il link d'invito o lo @username.")
                return

            folder = os.path.join('./download', parola.replace('#', ''))
            os.makedirs(folder, exist_ok=True)
            self.last_folder = folder

            # ---- Phase 1: collect candidates (with album expansion) ----
            self.log("Ricerca messaggi in corso...")
            self._set_status("Ricerca in corso...")
            candidati = {}
            gruppi_visti = set()

            async for message in self.client.iter_messages(self.entity, search=parola):
                if self.stop_event.is_set():
                    break
                msg_date = message.date.replace(tzinfo=None)
                if data_da and msg_date < data_da:
                    break
                if data_a and msg_date > data_a:
                    continue

                if message.grouped_id and message.grouped_id not in gruppi_visti:
                    # Album: fetch every item, including those without the hashtag.
                    gruppi_visti.add(message.grouped_id)
                    for fratello in await self._album_fratelli(message):
                        if self._da_scaricare(fratello, tipi_sel, exts):
                            candidati[fratello.id] = fratello
                elif self._da_scaricare(message, tipi_sel, exts):
                    candidati[message.id] = message

            messaggi = list(candidati.values())
            totale = len(messaggi)
            self.log(f"Trovati {totale} file corrispondenti.")

            # ---- Phase 2: download ----
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
