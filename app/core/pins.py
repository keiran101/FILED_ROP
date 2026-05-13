import json
from pathlib import Path

from app.core.config import settings


def _path() -> Path:
    return settings.upload_dir / ".pins.json"


def load() -> set:
    p = _path()
    if not p.exists():
        return set()
    try:
        return set(json.loads(p.read_text(encoding="utf-8")))
    except Exception:
        return set()


def _save(pins: set) -> None:
    _path().write_text(json.dumps(list(pins)), encoding="utf-8")


def toggle(filename: str) -> bool:
    pins = load()
    if filename in pins:
        pins.discard(filename)
        pinned = False
    else:
        pins.add(filename)
        pinned = True
    _save(pins)
    return pinned


def remove(filename: str) -> None:
    pins = load()
    pins.discard(filename)
    _save(pins)
