"""Stable artifact bytes; no environment-dependent formatting."""

import json
from pathlib import Path


def json_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json_bytes(value))


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))
