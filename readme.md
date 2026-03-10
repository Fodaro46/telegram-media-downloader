# 🎓 Telegram Student Downloader (GUI Version)

Un potente tool grafico in Python per automatizzare il recupero di dispense, PDF e materiali di studio da canali Telegram privati. Progettato per gli studenti che hanno bisogno di organizzare il materiale didattico filtrando per hashtag, data e tipologia di file.

![GitHub last commit](https://img.shields.io/github/last-commit/Fodaro46/telegram-media-downloader)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)

---

## ✨ Caratteristiche Principali

* **🖥️ Interfaccia Grafica (GUI):** Design moderno in Dark Mode (CustomTkinter) — addio terminale nero!
* **🔍 Ricerca Intelligente:** Scarica file basandosi su hashtag specifici (es. `#sistemi_operativi`).
* **📅 Filtro Temporale:** Scegli quanto andare a ritroso (1 mese, 6 mesi, 1 anno o tutto).
* **📁 Filtro Estensioni:** Scarica solo quello che ti serve (solo PDF/DOCX, solo Foto o solo Video).
* **📦 Gestione Album:** Riconosce i gruppi di foto/file e li scarica tutti insieme senza saltare nulla.
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

1.  Crea una cartella sul desktop e inserisci il file `main.exe`.
2.  Crea un file chiamato `.env` nella stessa cartella e incolla le tue credenziali:
    ```env
    API_ID=1234567
    API_HASH=tuo_codice_hash_alfanumerico
    ```
3.  Avvia `main.exe`.
4.  Inserisci l'hashtag, scegli i filtri e clicca su **AVVIA DOWNLOAD**.
5.  Se richiesto, inserisci il tuo numero di telefono e il codice che riceverai su Telegram nelle finestre di dialogo che appariranno.

---

## 📂 Struttura del Progetto

```text
.
├── main.py              # Codice sorgente con interfaccia CustomTkinter
├── .env                 # File locale (NON caricare su GitHub!)
├── .gitignore           # Esclude file sensibili e cartelle build
├── requirements.txt     # Dipendenze del progetto
└── download/            # Cartella generata automaticamente per i tuoi file