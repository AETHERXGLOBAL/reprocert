from __future__ import annotations

import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import __version__
from .certificate import CERT_API_VERSION, CERT_KIND, seal_certificate
from .claim import Claim
from .environment import capture_environment
from .util import json_pointer, sha256_bytes, sha256_file


class EvidenceResolutionError(RuntimeError):
    pass


def run_claim(claim: Claim) -> dict[str, Any]:
    spec = claim.spec
    base_dir = claim.path.parent
    working_dir = _safe_join(base_dir, str(spec.get("working_directory", ".")))
    if not working_dir.exists() or not working_dir.is_dir():
        raise EvidenceResolutionError(f"Working directory does not exist: {working_dir}")

    command = list(spec["command"])
    timeout = int(spec.get("timeout_seconds", 300))
    expected_exit_code = int(spec.get("expected_exit_code", 0))
    started = datetime.now(timezone.utc)
    start_perf = time.perf_counter()

    stdout = ""
    stderr = ""
    exit_code: int | None = None
    timed_out = False
    execution_error: str | None = None

    try:
        cp = subprocess.run(
            command,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
        )
        stdout = cp.stdout
        stderr = cp.stderr
        exit_code = cp.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = _to_text(exc.stdout)
        stderr = _to_text(exc.stderr)
        execution_error = f"Command timed out after {timeout}s"
    except OSError as exc:
        execution_error = f"Command could not start: {exc}"

    duration_ms = round((time.perf_counter() - start_perf) * 1000, 3)
    ended = datetime.now(timezone.utc)

    check_results: list[dict[str, Any]] = []
    resolution_errors: list[str] = []
    if execution_error is None:
        for check in spec["checks"]:
            try:
                observed = _resolve_source(check["source"], working_dir, stdout, stderr, exit_code)
                passed, reason = _evaluate(check, observed)
                check_results.append(
                    {
                        "id": check["id"],
                        "source": check["source"],
                        "op": check["op"],
                        "expected": check["expected"],
                        "abs_tolerance": check.get("abs_tolerance"),
                        "observed": observed,
                        "status": "PASS" if passed else "FAIL",
                        "reason": reason,
                    }
                )
            except Exception as exc:
                resolution_errors.append(f"{check['id']}: {exc}")
                check_results.append(
                    {
                        "id": check["id"],
                        "source": check["source"],
                        "op": check["op"],
                        "expected": check["expected"],
                        "abs_tolerance": check.get("abs_tolerance"),
                        "observed": None,
                        "status": "INCONCLUSIVE",
                        "reason": str(exc),
                    }
                )

    evidence_records, evidence_errors = _collect_evidence(spec.get("evidence", []), working_dir)
    resolution_errors.extend(evidence_errors)

    if execution_error is not None or timed_out or (exit_code is not None and exit_code != expected_exit_code):
        verdict = "ERROR"
    elif resolution_errors or any(c["status"] == "INCONCLUSIVE" for c in check_results):
        verdict = "INCONCLUSIVE"
    elif any(c["status"] == "FAIL" for c in check_results):
        verdict = "FAIL"
    else:
        verdict = "PASS"

    certificate: dict[str, Any] = {
        "apiVersion": CERT_API_VERSION,
        "kind": CERT_KIND,
        "metadata": {
            "claim_id": claim.claim_id,
            "title": claim.title,
            "generated_at": ended.isoformat(),
            "tool": "aetherx-reprocert",
            "tool_version": __version__,
        },
        "claim": {"path": claim.path.name, "sha256": claim.digest},
        "run": {
            "command": command,
            "working_directory": str(spec.get("working_directory", ".")),
            "timeout_seconds": timeout,
            "expected_exit_code": expected_exit_code,
            "started_at": started.isoformat(),
            "ended_at": ended.isoformat(),
            "duration_ms": duration_ms,
            "exit_code": exit_code,
            "timed_out": timed_out,
            "execution_error": execution_error,
            "stdout_sha256": sha256_bytes(stdout.encode("utf-8")),
            "stderr_sha256": sha256_bytes(stderr.encode("utf-8")),
            "stdout_excerpt": _excerpt(stdout),
            "stderr_excerpt": _excerpt(stderr),
        },
        "environment": capture_environment(working_dir),
        "checks": check_results,
        "evidence": evidence_records,
        "diagnostics": resolution_errors,
        "verdict": verdict,
    }
    return seal_certificate(certificate)


def _safe_join(base: Path, rel: str) -> Path:
    candidate = (base / rel).resolve()
    try:
        candidate.relative_to(base.resolve())
    except ValueError as exc:
        raise EvidenceResolutionError(f"Path escapes claim directory: {rel!r}") from exc
    return candidate


def _resolve_source(source: dict[str, Any], working_dir: Path, stdout: str, stderr: str, exit_code: int | None) -> Any:
    source_type = source["type"]
    if source_type == "stdout": return stdout
    if source_type == "stderr": return stderr
    if source_type == "exit_code": return exit_code
    path = _safe_join(working_dir, source["path"])
    if not path.is_file():
        raise EvidenceResolutionError(f"Required source file not found: {source['path']}")
    if source_type == "text": return path.read_text(encoding="utf-8")
    if source_type == "json":
        doc = json.loads(path.read_text(encoding="utf-8"))
        return json_pointer(doc, source.get("pointer", ""))
    if source_type == "file_sha256": return sha256_file(path)
    if source_type == "file_size": return path.stat().st_size
    raise EvidenceResolutionError(f"Unsupported source type: {source_type}")


def _evaluate(check: dict[str, Any], observed: Any) -> tuple[bool, str]:
    expected = check["expected"]
    op = check["op"]
    try:
        if op == "eq": passed = observed == expected
        elif op == "ne": passed = observed != expected
        elif op == "lt": passed = observed < expected
        elif op == "le": passed = observed <= expected
        elif op == "gt": passed = observed > expected
        elif op == "ge": passed = observed >= expected
        elif op == "approx": passed = abs(float(observed) - float(expected)) <= float(check["abs_tolerance"])
        elif op == "contains": passed = expected in observed
        else: raise ValueError(f"Unsupported operator: {op}")
    except (TypeError, ValueError) as exc:
        raise EvidenceResolutionError(f"Cannot evaluate {op}: {exc}") from exc
    return bool(passed), f"observed {observed!r} {op} expected {expected!r}"


def _collect_evidence(paths: list[str], working_dir: Path) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    for rel in paths:
        path = _safe_join(working_dir, rel)
        if not path.is_file():
            errors.append(f"evidence missing: {rel}")
            continue
        records.append({"path": rel, "sha256": sha256_file(path), "size": path.stat().st_size})
    records.sort(key=lambda x: x["path"])
    return records, errors


def _excerpt(text: str, limit: int = 4096) -> str:
    if len(text) <= limit: return text
    return text[:limit] + "\n…<truncated>"


def _to_text(value: Any) -> str:
    if value is None: return ""
    if isinstance(value, bytes): return value.decode("utf-8", errors="replace")
    return str(value)
