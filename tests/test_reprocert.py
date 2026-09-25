from __future__ import annotations

import json
from pathlib import Path

import pytest

from reprocert.claim import ClaimError, load_claim
from reprocert.runner import run_claim
from reprocert.verification import verify_certificate


def _write_project(tmp_path: Path, observed: int = 7, expected: int = 10) -> Path:
    (tmp_path / "produce.py").write_text("import json\njson.dump({'value': %d}, open('result.json','w'))\n" % observed, encoding="utf-8")
    claim = f"""apiVersion: reprocert.dev/v1alpha1
kind: ReproducibilityClaim
metadata:
  id: test-claim
  title: Test claim
spec:
  command: [python, produce.py]
  timeout_seconds: 30
  evidence: [result.json]
  checks:
    - id: value-under-limit
      source:
        type: json
        path: result.json
        pointer: /value
      op: lt
      expected: {expected}
"""
    path = tmp_path / "claim.yml"; path.write_text(claim, encoding="utf-8"); return path


def test_pass_and_verify(tmp_path: Path) -> None:
    claim_path=_write_project(tmp_path); cert=run_claim(load_claim(claim_path)); assert cert["verdict"]=="PASS"; assert cert["checks"][0]["observed"]==7; assert verify_certificate(cert,claim_path=claim_path,evidence_root=tmp_path)["status"]=="PASS"

def test_fail_is_claim_failure_not_execution_error(tmp_path: Path) -> None:
    cert=run_claim(load_claim(_write_project(tmp_path,12,10))); assert cert["verdict"]=="FAIL"; assert cert["run"]["exit_code"]==0

def test_missing_evidence_is_inconclusive(tmp_path: Path) -> None:
    path=_write_project(tmp_path); path.write_text(path.read_text().replace("evidence: [result.json]","evidence: [missing.json]"),encoding="utf-8"); assert run_claim(load_claim(path))["verdict"]=="INCONCLUSIVE"

def test_nonzero_process_is_error(tmp_path: Path) -> None:
    (tmp_path/"bad.py").write_text("raise SystemExit(9)\n",encoding="utf-8"); (tmp_path/"claim.yml").write_text("""apiVersion: reprocert.dev/v1alpha1
kind: ReproducibilityClaim
metadata: {id: bad}
spec:
  command: [python, bad.py]
  checks:
    - id: exit
      source: {type: exit_code}
      op: eq
      expected: 0
""",encoding="utf-8"); assert run_claim(load_claim(tmp_path/"claim.yml"))["verdict"]=="ERROR"

def test_tamper_detected(tmp_path: Path) -> None:
    cert=run_claim(load_claim(_write_project(tmp_path))); cert["checks"][0]["observed"]=999; assert verify_certificate(cert)["status"]=="FAIL"

def test_path_escape_rejected(tmp_path: Path) -> None:
    path=tmp_path/"claim.yml"; path.write_text("""apiVersion: reprocert.dev/v1alpha1
kind: ReproducibilityClaim
metadata: {id: escape}
spec:
  command: [python, x.py]
  evidence: [../secret.txt]
  checks:
    - id: x
      source: {type: stdout}
      op: contains
      expected: x
""",encoding="utf-8")
    with pytest.raises(ClaimError): load_claim(path)

def test_certificate_json_roundtrip(tmp_path: Path) -> None:
    cert=run_claim(load_claim(_write_project(tmp_path))); assert verify_certificate(json.loads(json.dumps(cert)))["status"]=="PASS"
