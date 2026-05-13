import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOG_DIR = Path("logs")
_LOG_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("filedrop")
logger.setLevel(logging.INFO)

_fmt = logging.Formatter("%(asctime)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

_fh = RotatingFileHandler(
    _LOG_DIR / "filedrop.log",
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8",
)
_fh.setFormatter(_fmt)
logger.addHandler(_fh)

_ch = logging.StreamHandler()
_ch.setFormatter(_fmt)
logger.addHandler(_ch)


def _fmt_size(b: int) -> str:
    if b < 1024:
        return f"{b} B"
    if b < 1024 ** 2:
        return f"{b / 1024:.1f} KB"
    if b < 1024 ** 3:
        return f"{b / 1024 ** 2:.1f} MB"
    return f"{b / 1024 ** 3:.2f} GB"


def log_upload(ip: str, filename: str, size: int) -> None:
    logger.info("UPLOAD   | %-15s | %s | %s", ip, filename, _fmt_size(size))


def log_download(ip: str, filename: str, size: int) -> None:
    logger.info("DOWNLOAD | %-15s | %s | %s", ip, filename, _fmt_size(size))


def log_delete(ip: str, filename: str) -> None:
    logger.info("DELETE   | %-15s | %s", ip, filename)
