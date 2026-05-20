import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

_initialized = False


def setup_logging() -> None:
    global _initialized
    if _initialized:
        return

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / "trading_bot.log"

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(module)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    _initialized = True
