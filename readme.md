# 🎓 Telegram Student Downloader (GUI Version)

A powerful Python GUI tool to automate the retrieval of lecture notes, PDFs and study materials from private Telegram channels. Built for students who need to organize course material by filtering on hashtag, date and file type.

> The graphical interface is in Italian, since the tool targets Italian university students.

![GitHub last commit](https://img.shields.io/github/last-commit/Fodaro46/telegram-media-downloader)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)

---

## ✨ Key Features

* **🖥️ Graphical Interface (GUI):** Modern dark-mode design (CustomTkinter) with sections, progress bar and a real-time log.
* **⚙️ In-app configuration:** Enter your API ID, API Hash and target channel directly from the GUI — no code editing required.
* **🔍 Smart Search:** Download files based on specific hashtags (e.g. `#operating_systems`).
* **📦 Full albums:** If the hashtag is only on one photo/document of a grouped message, the tool fetches and downloads **all** attachments of the album, even those without the hashtag.
* **📅 Time Filter:** Quick presets (from 1 month up to 4 years, or the whole history) **or** a precise `From / To` range in `DD/MM/YYYY` format. Manual dates take priority over the preset.
* **📁 Multiple file types:** Multi-select checkboxes — Documents, Photos, Videos, Audio, Voice messages, Archives (zip/rar/7z…), GIFs.
* **🔎 Extension filter:** Optional field (e.g. `pdf, docx, zip`) to download only specific formats, combinable with the type selection.
* **♻️ Duplicate skipping:** Already-downloaded files are skipped automatically (no double downloads).
* **⛔ Stop & progress:** Button to safely interrupt, progress bar and an "Open folder" button.
* **🔐 Secure Login:** Verification code and 2FA password handled directly in the app.

---

## 🛠️ Requirements (for Developers)

To run the source code (`main.py`) you need:

1.  **Python 3.9+**
2.  **API Keys:** Get your `API_ID` and `API_HASH` at [my.telegram.org](https://my.telegram.org).
3.  **Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## 🚀 How to use it (Student Guide)

If you downloaded the `.exe` executable:

1.  Launch `main.exe`.
2.  In the **⚙️ Configuration** tab, fill in:
    * **API ID** and **API Hash** (get them at [my.telegram.org](https://my.telegram.org) → *API development tools*);
    * **Channel**: paste the invite link (`https://t.me/+...`), the `@username` or the numeric ID (`-100...`). If it is an invite link, the bot joins the channel by itself.
    * Press **💾 Save configuration** (your data stays only on your PC, in `config.json`).
3.  Switch to the **⬇️ Download** tab, enter the hashtag, choose the filters and click **START DOWNLOAD**.
4.  On first launch, enter your phone number and the code you receive on Telegram in the dialog windows that appear (and the 2FA password if enabled).

> All configuration is done from the interface: you no longer need to edit the code or create files by hand.

---

## 📂 Project Structure

```text
.
├── main.py              # Source code with the CustomTkinter interface
├── config.json          # Local config: API keys + channel (NOT committed to GitHub!)
├── .env                 # Optional local file for API keys (NOT committed!)
├── .gitignore           # Excludes sensitive files and build folders
├── requirements.txt     # Project dependencies
└── download/            # Auto-generated folder for your files
```

---

## 🔐 Security note

`config.json`, `.env` and the Telegram `*.session` files contain credentials and session data: they are listed in `.gitignore` and must **never** be pushed to GitHub.
