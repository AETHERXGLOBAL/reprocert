from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from . import __version__
from .claim import ClaimError, load_claim
from .runner import run_claim
from .util import canonical_json_bytes, sha256_bytes

SUITE_API_VERSION = "reprocert.dev/suite/v1alpha1"
SUITE_KIND = "ReproCertSuite"


class SuiteError(ValueError):
    pass


@dataclass(frozen=True)
class Suite:
    raw: dict[str, Any]
    path: Path

    @property
    def metadata(self) -> dict[str, Any]:
        return self.raw["metadata"]

    @property
    def spec(self) -> dict[str, Any]:
        return self.raw["spec"]

    @property
    def suite_id(self) -> str:
        return str(self.metadata["id"])


def load_suite(path: str | Path) -> Suite:
    suite_path = Path(path).resolve()
    try:
        text = suite_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SuiteError(f"Cannot read suite file: {exc}") from exc

    try:
        raw = json.loads(text) if suite_path.suffix.lower() == ".json" else yaml.safe_load(text)
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise SuiteError(f"Invalid suite syntax: {exc}") from exc

    if not isinstance(raw, dict):
        raise SuiteError("Suite root must be an object")
    validate_suite(raw)
    return Suite(raw=raw, path=suite_path)


def validate_suite(raw: dict[str, Any]) -> None:
    if raw.get("apiVersion") != SUITE_API_VERSION:
        raise SuiteError(f"apiVersion must be {SUITE_API_VERSION!r}")
    if raw.get("kind") != SUITE_KIND:
        raise SuiteError(f"kind must be {SUITE_KIND!r}")

    metadata = raw.get("metadata")
    spec = raw.get("spec")
    if not isinstance(metadata, dict) or not metadata.get("id"):
        raise SuiteError("metadata.id is required")
    if not isinstance(spec, dict):
        raise SuiteError("spec must be an object")

    claims = spec.get("claims")
    if not isinstance(claims, list) or not claims:
        raise SuiteError("spec.claims must contain at least one relative claim path")
    for rel in claims:
        if not isinstance(rel, str) or not rel:
            raise SuiteError("suite claim paths must be non-empty strings")
        p = Path(rel)
        if p.is_absolute() or ".." in p.parts:
            raise SuiteError(f"suite claim path must stay inside the suite directory: {rel!r}")


def run_suite(suite: Suite) -> tuple[dict[str, Any], list[tuple[str, dict[str, Any]]]]:
    base = suite.path.parent.resolve()
    certificates: list[tuple[str, dict[str, Any]]] = []
    entries: list[dict[str, Any]] = []

    for rel in suite.spec["claims"]:
        claim_path = (base / rel).resolve()
        try:
            claim_path.relative_to(base)
        except ValueError as exc:
            raise SuiteError(f"suite claim path escapes suite directory: {rel!r}") from exc

        try:
            claim = load_claim(claim_path)
        except ClaimError as exc:
            raise SuiteError(f"{rel}: {exc}") from exc

        certificate = run_claim(claim)
        certificates.append((rel, certificate))
        entries.append(
            {
                "claim_path": rel,
                "claim_id": certificate["metadata"]["claim_id"],
                "verdict": certificate["verdict"],
                "certificate_sha256": certificate["integrity"]["certificate_sha256"],
            }
        )

    verdict = _aggregate_verdict([entry["verdict"] for entry in entries])
    report: dict[str, Any] = {
        "apiVersion": "reprocert.dev/suite-report/v1alpha1",
        "kind": "ReproCertSuiteReport",
        "metadata": {
            "suite_id": suite.suite_id,
            "title": suite.metadata.get("title", suite.suite_id),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "tool": "aetherx-reprocert",
            "tool_version": __version__,
        },
        "suite": {
            "path": suite.path.name,
            "sha256": sha256_bytes(canonical_json_bytes(suite.raw)),
        },
        "claims": entries,
        "verdict": verdict,
    }
    report["integrity"] = {
        "algorithm": "sha256",
        "canonicalization": "JSON_SORTED_KEYS_UTF8_V1",
    }
    report["integrity"]["report_sha256"] = _report_digest(report)
    return report, certificates


def _aggregate_verdict(verdicts: list[str]) -> str:
    if any(verdict == "FAIL" for verdict in verdicts):
        return "FAIL"
    if any(verdict == "ERROR" for verdict in verdicts):
        return "ERROR"
    if any(verdict == "INCONCLUSIVE" for verdict in verdicts):
        return "INCONCLUSIVE"
    return "PASS"


def _report_digest(report: dict[str, Any]) -> str:
    material = json.loads(json.dumps(report))
    material.get("integrity", {}).pop("report_sha256", None)
    return sha256_bytes(canonical_json_bytes(material))
