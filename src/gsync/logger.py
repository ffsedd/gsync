import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str,
    level: int = logging.INFO,
    console: bool = True,
    log_file: Optional[Path] = None,
) -> logging.Logger:
    """
    Configure and return a named logger with optional console and file output.

    - Console output includes colored log level names for INFO, WARNING, ERROR, and CRITICAL.
    - File output includes a simpler uncolored format with numeric log level.

    Args:
        name: The name of the logger to retrieve or create.
        level: Logging level to capture (default: logging.INFO).
        console: Whether to enable logging to the console (default: True).
        log_file: Optional path to a log file (default: None).

    Returns:
        A configured `logging.Logger` instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # Prevent duplicate logs from parent loggers

    if logger.handlers:
        return logger  # Avoid re-adding handlers if already configured

    if log_file:
        file_formatter = logging.Formatter(
            "%(asctime)s [%(module)10s:%(lineno)3d] !%(levelno)2d  %(message)s"
        )
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    if console:
        # Add ANSI color codes for level names
        logging.addLevelName(logging.INFO, f"\033[92m{logging.getLevelName(logging.INFO)}\033[0m")
        logging.addLevelName(
            logging.WARNING, f"\033[33m{logging.getLevelName(logging.WARNING)}\033[0m"
        )
        logging.addLevelName(
            logging.ERROR, f"\033[31m{logging.getLevelName(logging.ERROR)}\033[0m"
        )
        logging.addLevelName(
            logging.CRITICAL, f"\033[41m{logging.getLevelName(logging.CRITICAL)}\033[0m"
        )

        console_formatter = logging.Formatter(
            "%(asctime)s [%(module)10s:%(lineno)3d] %(levelname)8s  %(message)s",
            datefmt="%H:%M:%S",
        )
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger


if __name__ == "__main__":
    logger = setup_logger("report", level=logging.DEBUG)
    logger.info("Log started...")
