from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def json_pointer(document: Any, pointer: str) -> Any:
    if pointer in ("", "/"):
        return document if pointer == "" else _pointer_step(document, "")
    if not pointer.startswith("/"):
        raise ValueError("JSON pointer must be empty or start with '/'")
    value = document
    for raw in pointer.split("/")[1:]:
        token = raw.replace("~1", "/").replace("~0", "~")
        value = _pointer_step(value, token)
    return value


def _pointer_step(value: Any, token: str) -> Any:
    if isinstance(value, list):
        try:
            index = int(token)
        except ValueError as exc:
            raise KeyError(f"List pointer token is not an integer: {token!r}") from exc
        return value[index]
    if isinstance(value, dict):
        return value[token]
    raise KeyError(f"Cannot descend through {type(value).__name__}")
