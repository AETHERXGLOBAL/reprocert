from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .util import canonical_json_bytes, sha256_bytes

CLAIM_API_VERSION = "reprocert.dev/v1alpha1"
CLAIM_KIND = "ReproducibilityClaim"


class ClaimError(ValueError):
    pass


@dataclass(frozen=True)
class Claim:
    raw: dict[str, Any]
    path: Path

    @property
    def metadata(self) -> dict[str, Any]:
        return self.raw["metadata"]

    @property
    def spec(self) -> dict[str, Any]:
        return self.raw["spec"]

    @property
    def claim_id(self) -> str:
        return str(self.metadata["id"])

    @property
    def title(self) -> str:
        return str(self.metadata.get("title", self.claim_id))

    @property
    def digest(self) -> str:
        return sha256_bytes(canonical_json_bytes(self.raw))


def load_claim(path: str | Path) -> Claim:
    claim_path = Path(path).resolve()
    try:
        text = claim_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ClaimError(f"Cannot read claim file: {exc}") from exc

    try:
        if claim_path.suffix.lower() == ".json":
            raw = json.loads(text)
        else:
            raw = yaml.safe_load(text)
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise ClaimError(f"Invalid claim syntax: {exc}") from exc

    if not isinstance(raw, dict):
        raise ClaimError("Claim root must be an object")
    validate_claim(raw)
    return Claim(raw=raw, path=claim_path)


def validate_claim(raw: dict[str, Any]) -> None:
    if raw.get("apiVersion") != CLAIM_API_VERSION:
        raise ClaimError(f"apiVersion must be {CLAIM_API_VERSION!r}")
    if raw.get("kind") != CLAIM_KIND:
        raise ClaimError(f"kind must be {CLAIM_KIND!r}")

    metadata = raw.get("metadata")
    spec = raw.get("spec")
    if not isinstance(metadata, dict) or not metadata.get("id"):
        raise ClaimError("metadata.id is required")
    if not isinstance(spec, dict):
        raise ClaimError("spec must be an object")

    command = spec.get("command")
    if not isinstance(command, list) or not command or not all(isinstance(x, str) and x for x in command):
        raise ClaimError("spec.command must be a non-empty array of strings")

    timeout = spec.get("timeout_seconds", 300)
    if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout < 1 or timeout > 86400:
        raise ClaimError("spec.timeout_seconds must be an integer between 1 and 86400")

    evidence = spec.get("evidence", [])
    if not isinstance(evidence, list) or not all(isinstance(x, str) and x for x in evidence):
        raise ClaimError("spec.evidence must be an array of relative file paths")
    for rel in evidence:
        _validate_relative_path(rel, "evidence")

    checks = spec.get("checks", [])
    if not isinstance(checks, list) or not checks:
        raise ClaimError("spec.checks must contain at least one check")
    seen: set[str] = set()
    for check in checks:
        if not isinstance(check, dict):
            raise ClaimError("Each check must be an object")
        check_id = check.get("id")
        if not isinstance(check_id, str) or not check_id:
            raise ClaimError("Each check requires a non-empty id")
        if check_id in seen:
            raise ClaimError(f"Duplicate check id: {check_id}")
        seen.add(check_id)
        source = check.get("source")
        if not isinstance(source, dict):
            raise ClaimError(f"Check {check_id}: source must be an object")
        source_type = source.get("type")
        if source_type not in {"json", "text", "stdout", "stderr", "exit_code", "file_sha256", "file_size"}:
            raise ClaimError(f"Check {check_id}: unsupported source type {source_type!r}")
        if source_type in {"json", "text", "file_sha256", "file_size"}:
            path = source.get("path")
            if not isinstance(path, str) or not path:
                raise ClaimError(f"Check {check_id}: source.path is required")
            _validate_relative_path(path, f"check {check_id} source")
        if source_type == "json" and not isinstance(source.get("pointer", ""), str):
            raise ClaimError(f"Check {check_id}: source.pointer must be a string")

        op = check.get("op")
        if op not in {"eq", "ne", "lt", "le", "gt", "ge", "approx", "contains"}:
            raise ClaimError(f"Check {check_id}: unsupported op {op!r}")
        if "expected" not in check:
            raise ClaimError(f"Check {check_id}: expected is required")
        if op == "approx":
            tol = check.get("abs_tolerance")
            if not isinstance(tol, (int, float)) or isinstance(tol, bool) or tol < 0:
                raise ClaimError(f"Check {check_id}: abs_tolerance must be a non-negative number")


def _validate_relative_path(value: str, label: str) -> None:
    p = Path(value)
    if p.is_absolute() or ".." in p.parts:
        raise ClaimError(f"{label} path must stay inside the working directory: {value!r}")
