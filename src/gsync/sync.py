import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import gspread
import pandas as pd  # type: ignore

from gsync.client import authorize_gspread
from gsync.config import CREDENTIALS_FILE_PATH, GSHEET_IDS, get_temp_dir
from gsync.logger import setup_logger

logger = setup_logger("report", level=10)
logger.info("Log started...")

TEMP_DPATH = get_temp_dir()
logger.info(f"Temporary directory: {TEMP_DPATH}")


class gSync:
    def __init__(
        self,
        ssid: str,
        name: str,
        sheet_name: Optional[str] = None,
        fpath: Optional[Path] = None,
        index_col: Optional[int] = 0,
        client: Optional[gspread.Client] = None,
    ):
        self.name = name
        self.fpath = Path(fpath) if fpath else TEMP_DPATH / f"{name}.xlsx"
        self.index_col = index_col
        self._df = None

        self.fpath.parent.mkdir(parents=True, exist_ok=True)
        if self.fpath.suffix not in (".tsv", ".xlsx", ".json"):
            raise ValueError(f"Unsupported file extension: {self.fpath.suffix}")

        self.gc = client or authorize_gspread()
        self.book = self.gc.open_by_key(ssid)
        self.ws = (
            self.book.worksheet(sheet_name)
            if sheet_name
            else self.book.get_worksheet(0)
        )

        self._last_update_time: Optional[datetime] = None

        logger.debug(
            f"SyncSheet initialized: name={self.name}, file={self.fpath}, ssid={ssid}"
        )

    def is_synced(self) -> bool:
        """Compare local file timestamp with Google Sheet last update."""
        if not self.fpath.exists():
            logger.info(f"File missing: {self.fpath}")
            return False
        try:
            file_time = datetime.fromtimestamp(self.fpath.stat().st_mtime)
            diff = abs((file_time - self.last_update_time).total_seconds())
            logger.debug(
                f"{self.name}: file_time={file_time}, sheet_time={self.last_update_time}, diff={diff:.1f}s"
            )
            return diff < 10  # consider synced if within 10 seconds
        except Exception as e:
            logger.warning(f"Timestamp check failed: {e}")
            return False

    def download(self, skip_header: int = 0, force: bool = False):
        """Download Google Sheet into DataFrame and save it locally."""
        if not force and self.is_synced():
            logger.info(f"{self.name}: Up to date. Skipping download.")
            return

        logger.info(f"{self.name}: Downloading from Google Sheets → {self.fpath}")
        records = self.ws.get_all_records(value_render_option="FORMATTED_VALUE")  # type: ignore
        self._df = pd.DataFrame(records[skip_header:])
        self.set_index()
        self.save()

    def save(self):
        """Save DataFrame to .tsv, .xlsx, or .json and update timestamp."""
        logger.info(f"{self.name}: Saving to {self.fpath}")
        if self.fpath.suffix == ".tsv":
            self.df.to_csv(self.fpath, sep="\t")
        elif self.fpath.suffix == ".xlsx":
            self.df.to_excel(self.fpath)
        elif self.fpath.suffix == ".json":
            self.df.to_json(self.fpath, orient="records", indent=2)

        # Set file modified time to match sheet timestamp
        ts = datetime.timestamp(self.last_update_time)
        os.utime(self.fpath, (ts, ts))

    def load(self):
        """Load DataFrame from local file."""
        logger.debug(f"{self.name}: Loading from {self.fpath}")
        if self.fpath.suffix == ".tsv":
            self._df = pd.read_csv(self.fpath, sep="\t")
        elif self.fpath.suffix == ".xlsx":
            self._df = pd.read_excel(self.fpath)
        elif self.fpath.suffix == ".json":
            self._df = pd.read_json(self.fpath)

        self.set_index()

    def set_index(self):
        if self.index_col is not None and self._df is not None:
            try:
                self._df.set_index(self._df.columns[self.index_col], inplace=True)
            except IndexError:
                logger.warning(
                    f"{self.name}: Invalid index_col={self.index_col}, skipping set_index"
                )

    @property
    def df(self) -> pd.DataFrame:
        """Return DataFrame, loading or downloading if necessary."""
        if self._df is None:
            if self.is_synced():
                self.load()
            else:
                self.download()
        return self._df

    @property
    def last_update_time(self) -> datetime:
        """Cached access to Google Sheet last update time.

        Returns:
            datetime: Last updated time of the sheet, parsed from ISO format.
        """
        if self._last_update_time is not None:
            return self._last_update_time

        try:
            stamp = self.book.get_lastUpdateTime()
            try:
                # Try full format with microseconds
                self._last_update_time = datetime.strptime(
                    stamp, "%Y-%m-%dT%H:%M:%S.%fZ"
                )
            except ValueError:
                # Fallback for timestamps without microseconds
                self._last_update_time = datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ")
        except Exception as e:
            logger.warning(f"Failed to retrieve last update time for {self.name}: {e}")
            self._last_update_time = datetime.now()

        return self._last_update_time

    def __repr__(self):
        return f"<SyncSheet name={self.name!r} fpath={str(self.fpath)} synced={self.is_synced()}>"


if __name__ == "__main__":
    client = authorize_gspread(CREDENTIALS_FILE_PATH)
    sheet_name = "zakazky"
    ssid = GSHEET_IDS[sheet_name]
    sheet = gSync(
        ssid=ssid,
        name=sheet_name,
        fpath=TEMP_DPATH / (f"{sheet_name}.tsv"),
        client=client,
    )
    sheet.download()
    print(sheet.df)
    print(
        f"Last update time: {sheet.last_update_time.isoformat()}"
        if sheet.last_update_time
        else "Not available"
    )
    print(f"Synced: {sheet.is_synced()}")
