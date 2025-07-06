# gsync

A lightweight Python utility to synchronize editable Google Sheets with local cached files (TSV, Excel, JSON).  
Designed for offline LaTeX report generation, scientific data workflows, and efficient project automation.

## ✨ Features

- Access Google Sheets via `gspread` with a service account
- Automatically download sheets and cache them locally
- Supports `.tsv`, `.xlsx`, `.json` formats
- Avoids unnecessary downloads using timestamp comparison
- Easily sync multiple sheets via `SyncManager`

## 📦 Installation

```bash
git clone https://github.com/YOUR_USERNAME/gsync.git
cd gsync
uv venv  # or python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## ⚙️ Configuration

Secrets and config are stored in:

- `secrets/credentials.json` — your Google service account credentials (not tracked in Git)
- `gsync/config.py` — includes Google Sheet IDs, scopes, and temp directory logic

Example config entry:

```python
GSHEET_IDS = {
    "zakazky": "1A9y...",
    "vzorky": "1hsNF...",
}
```




## 📁 Project Structure

```
gsync/
├── src/gsync/
│   ├── sync.py
│   ├── client.py
│   ├── config.py
│   └── logger.py
├── secrets/
│   └── credentials.json   # ← excluded via .gitignore
├── README.md
├── pyproject.toml
├── uv.lock

```

## 📝 License

GPL-3.0-or-later

---

Made with ☕ and Google Sheets.