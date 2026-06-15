# 🎓 Telegram Student Downloader (GUI Version)

Un potente tool grafico in Python per automatizzare il recupero di dispense, PDF e materiali di studio da canali Telegram privati. Progettato per gli studenti che hanno bisogno di organizzare il materiale didattico filtrando per hashtag, data e tipologia di file.

![GitHub last commit](https://img.shields.io/github/last-commit/Fodaro46/telegram-media-downloader)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)

---

## ✨ Caratteristiche Principali

* **🖥️ Interfaccia Grafica (GUI):** Design moderno in Dark Mode (CustomTkinter) con sezioni, barra di avanzamento e log in tempo reale.
* **🔍 Ricerca Intelligente:** Scarica file basandosi su hashtag specifici (es. `#sistemi_operativi`).
* **📦 Album completi:** Se l'hashtag è presente solo su una foto/documento di un gruppo, recupera e scarica **tutti** gli allegati dell'album, anche quelli senza hashtag.
* **📅 Filtro Temporale:** Preset rapidi (da 1 mese fino a 4 anni o tutto lo storico) **oppure** un intervallo preciso `Da / A` in formato `GG/MM/AAAA`. Se compili le date manuali, hanno la priorità sul preset.
* **📁 Tipi file multipli:** Selezione multipla con checkbox — Documenti, Foto, Video, Audio, Vocali, Archivi (zip/rar/7z…), GIF.
* **🔎 Filtro per estensione:** Campo opzionale (es. `pdf, docx, zip`) per scaricare solo certi formati, combinabile con i tipi.
* **♻️ Skip duplicati:** I file già scaricati vengono saltati automaticamente (niente download doppi).
* **⛔ Stop & progresso:** Pulsante per interrompere in sicurezza, barra di avanzamento e pulsante "Apri cartella".
* **🔐 Login Sicuro:** Gestione del codice di verifica e della Password 2FA direttamente dall'app.

---

## 🛠️ Requisiti per gli Sviluppatori

Se vuoi far girare il codice sorgente (`main.py`), avrai bisogno di:

1.  **Python 3.9+**
2.  **API Keys:** Ottieni le tue `API_ID` e `API_HASH` su [my.telegram.org](https://my.telegram.org).
3.  **Librerie:**
    ```bash
    pip install telethon customtkinter python-dotenv
    ```

---

## 🚀 Come usarlo (Guida per gli Studenti)

Se hai scaricato l'eseguibile `.exe`:

1.  Avvia `main.exe`.
2.  Nella scheda **⚙️ Configurazione** inserisci:
    * **API ID** e **API Hash** (li ottieni su [my.telegram.org](https://my.telegram.org) → *API development tools*);
    * **Canale**: incolla il link d'invito (`https://t.me/+...`), lo `@username` oppure l'ID numerico (`-100...`). Se è un link d'invito, il bot entra nel canale da solo.
    * Premi **💾 Salva configurazione** (i dati restano solo sul tuo PC, in `config.json`).
3.  Passa alla scheda **⬇️ Download**, inserisci l'hashtag, scegli i filtri e clicca su **AVVIA DOWNLOAD**.
4.  Al primo avvio inserisci il tuo numero di telefono e il codice che riceverai su Telegram nelle finestre di dialogo che appariranno (e la password 2FA se attiva).

> Tutta la configurazione si fa dall'interfaccia: non serve più modificare il codice o creare file a mano.

---

## 📂 Struttura del Progetto

```text
.
├── main.py              # Codice sorgente con interfaccia CustomTkinter
├── .env                 # File locale (NON caricare su GitHub!)
├── .gitignore           # Esclude file sensibili e cartelle build
├── requirements.txt     # Dipendenze del progetto
└── download/            # Cartella generata automaticamente per i tuoi file