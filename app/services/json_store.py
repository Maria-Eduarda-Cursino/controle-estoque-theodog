"""Leitura/escrita JSON com escrita atômica (adequado ao Windows)."""

from __future__ import annotations

import json
import os
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def data_dir() -> Path:
    return _DATA_DIR


def ensure_data_dir() -> None:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)


def path_for(filename: str) -> Path:
    return _DATA_DIR / filename


def read_json(filename: str, default):
    ensure_data_dir()
    path = path_for(filename)
    if not path.exists():
        write_json_atomic(filename, default)
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json_atomic(filename: str, data) -> None:
    ensure_data_dir()
    path = path_for(filename)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)
