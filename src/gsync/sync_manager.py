from dataclasses import dataclass
from typing import List
from gsync.sync import gSync
from gsync.client import authorize_gspread
from gsync.config import TEMP_DPATH, GSHEET_IDS, CREDENTIALS_FILE_PATH


@dataclass
class SyncManager:
    sheets: List[gSync]

    def sync_all(self, force: bool = False) -> None:
        for sheet in self.sheets:
            sheet.fpath.parent.mkdir(parents=True, exist_ok=True)
            sheet.download(force=force)


if __name__ == "__main__":

    client = authorize_gspread(CREDENTIALS_FILE_PATH)

    sheets = [
        gSync(
            ssid=ssid,
            name=sheet_name,
            fpath=TEMP_DPATH / f"{sheet_name}.tsv",
            client=client,
        )
        for sheet_name, ssid in GSHEET_IDS.items()
    ]

    manager = SyncManager(sheets)
    manager.sync_all(force=False)

    for sheet in manager.sheets:
        print(f"{sheet.name}: {sheet.is_synced()}")
