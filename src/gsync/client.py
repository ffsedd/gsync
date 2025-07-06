import gspread
from oauth2client.service_account import ServiceAccountCredentials  # type: ignore
from pathlib import Path
from typing import Optional


def authorize_gspread(
    credentials_path: Optional[Path] = None,
    scopes: Optional[list[str]] = None,
) -> gspread.Client:
    """
    Authorize and return a gspread client using a service account JSON.

    Args:
        credentials_path: Path to the service account JSON key file.
                          If None, defaults to 'secrets/service_account.json'.
        scopes: List of OAuth2 scopes. Defaults to Google Sheets and Drive scopes.

    Returns:
        gspread.Client: Authorized client to access Google Sheets.
    """
    if credentials_path is None:
        credentials_path = Path("secrets/service_account.json")

    if scopes is None:
        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(str(credentials_path), scopes)
    client = gspread.authorize(creds)
    return client
