from pathlib import Path
import tempfile

GSHEET_IDS = {
    "zakazky": "1A9yRIG3ilZ9S9JDAMxzfhLtY4yhd5UcaJHyNzR5Lmm4",
    "vzorky": "1hsNFcPR9xKE9fNVzbbH4RhAhzbvhot72byn7DygcGm4",
    "objednavky": "1qE24ivELb-Qrp5iBL0zgnnnlkQJYrKAS2Ed33_iftW8",
}

CREDENTIALS_FILE_PATH = Path(__file__).parent.parent.parent / "secrets/service_account.json"
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]

# Default location to save synced files
TEMP_DPATH = Path(tempfile.gettempdir()) / "gsync"
TEMP_DPATH.mkdir(parents=True, exist_ok=True)


if not CREDENTIALS_FILE_PATH.exists():
    raise FileNotFoundError(f"Service account credentials file not found: {CREDENTIALS_FILE_PATH}")


def get_temp_dir() -> Path:
    TEMP_DPATH.mkdir(parents=True, exist_ok=True)
    return TEMP_DPATH
