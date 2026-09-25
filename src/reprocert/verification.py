from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .certificate import CERT_API_VERSION, CERT_KIND, compute_certificate_digest
from .claim import load_claim
from .util import sha256_file


def load_certificate(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    raw = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Certificate root must be an object")
    if raw.get("apiVersion") != CERT_API_VERSION or raw.get("kind") != CERT_KIND:
        raise ValueError("Unsupported certificate format")
    return raw


def verify_certificate(certificate: dict[str, Any], *, claim_path: str | Path | None = None, evidence_root: str | Path | None = None) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    recorded = certificate.get("integrity", {}).get("certificate_sha256")
    computed = compute_certificate_digest(certificate)
    checks.append(_result("certificate_digest", recorded == computed, recorded, computed))
    logical = _expected_verdict(certificate)
    checks.append(_result("verdict_consistency", certificate.get("verdict") == logical, certificate.get("verdict"), logical))
    if claim_path is not None:
        claim = load_claim(claim_path)
        expected = certificate.get("claim", {}).get("sha256")
        checks.append(_result("claim_digest", expected == claim.digest, expected, claim.digest))
    if evidence_root is not None:
        root = Path(evidence_root).resolve()
        for record in certificate.get("evidence", []):
            rel = record.get("path")
            if not isinstance(rel, str):
                checks.append(_result("evidence_path", False, rel, "relative string")); continue
            path = (root / rel).resolve()
            try: path.relative_to(root)
            except ValueError:
                checks.append(_result(f"evidence:{rel}", False, record.get("sha256"), "path escaped root")); continue
            if not path.is_file():
                checks.append(_result(f"evidence:{rel}", False, record.get("sha256"), "missing")); continue
            actual = sha256_file(path)
            checks.append(_result(f"evidence:{rel}", actual == record.get("sha256"), record.get("sha256"), actual))
    passed = all(c["status"] == "PASS" for c in checks)
    return {"status":"PASS" if passed else "FAIL","checks":checks,"trust_boundary":"This verification checks certificate structure, internal consistency, and optional local file digests. It does not authenticate the producer. Verify a separate signed CI attestation when producer identity matters."}


def _expected_verdict(cert: dict[str, Any]) -> str:
    run=cert.get("run", {})
    if run.get("execution_error") or run.get("timed_out"): return "ERROR"
    if run.get("exit_code") != run.get("expected_exit_code",0): return "ERROR"
    checks=cert.get("checks",[])
    if cert.get("diagnostics") or any(c.get("status")=="INCONCLUSIVE" for c in checks): return "INCONCLUSIVE"
    if any(c.get("status")=="FAIL" for c in checks): return "FAIL"
    return "PASS"


def _result(name: str, passed: bool, expected: Any, observed: Any) -> dict[str, Any]:
    return {"name":name,"status":"PASS" if passed else "FAIL","expected":expected,"observed":observed}
