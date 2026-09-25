from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from reprocert.claim import ClaimError, load_claim
from reprocert.container import (
    ContainerProfileError,
    build_docker_command,
    validate_container_profile,
)
from reprocert.policy import evaluate_policy, load_policy
from reprocert.pytest_adapter import run_pytest_adapter
from reprocert.runner import run_claim
from reprocert.verification import verify_certificate


def test_accepted_exit_code_can_still_produce_fail(tmp_path: Path) -> None:
    (tmp_path / "run.py").write_text(
        "from pathlib import Path\n"
        "Path('value.txt').write_text('bad', encoding='utf-8')\n"
        "raise SystemExit(1)\n",
        encoding="utf-8",
    )
    claim = tmp_path / "claim.yml"
    claim.write_text(
        """apiVersion: reprocert.dev/v1alpha1
kind: ReproducibilityClaim
metadata: {id: accepted-exit}
spec:
  command: [python, run.py]
  accepted_exit_codes: [0, 1]
  evidence: [value.txt]
  checks:
    - id: value
      source: {type: text, path: value.txt}
      op: eq
      expected: good
""",
        encoding="utf-8",
    )

    certificate = run_claim(load_claim(claim))
    assert certificate["run"]["exit_code"] == 1
    assert certificate["verdict"] == "FAIL"
    assert verify_certificate(
        certificate,
        claim_path=claim,
        evidence_root=tmp_path,
    )["status"] == "PASS"


def test_exit_code_contracts_cannot_be_ambiguous(tmp_path: Path) -> None:
    claim = tmp_path / "claim.yml"
    claim.write_text(
        """apiVersion: reprocert.dev/v1alpha1
kind: ReproducibilityClaim
metadata: {id: ambiguous}
spec:
  command: [python, x.py]
  expected_exit_code: 0
  accepted_exit_codes: [0, 1]
  checks:
    - id: x
      source: {type: stdout}
      op: contains
      expected: x
""",
        encoding="utf-8",
    )
    with pytest.raises(ClaimError):
        load_claim(claim)


def test_mutable_container_tag_is_rejected() -> None:
    with pytest.raises(ContainerProfileError):
        validate_container_profile({"image": "python:3.13"})


@pytest.mark.skipif(
    not hasattr(os, "getuid") or not hasattr(os, "getgid"),
    reason="hardened container command currently requires a POSIX host",
)
def test_container_command_is_hardened(tmp_path: Path) -> None:
    digest = "a" * 64
    profile = validate_container_profile(
        {"image": f"example.invalid/repro@sha256:{digest}"}
    )
    command = build_docker_command(
        profile,
        tmp_path,
        ["python", "job.py"],
    )
    joined = " ".join(command)
    assert "--network none" in joined
    assert "--read-only" in command
    assert "--cap-drop ALL" in joined
    assert "no-new-privileges:true" in command
    assert "--user" in command
    assert any(
        item.endswith(f"@sha256:{digest}")
        for item in command
    )


def test_policy_is_separate_from_certificate_verdict(tmp_path: Path) -> None:
    (tmp_path / "produce.py").write_text(
        "from pathlib import Path\n"
        "Path('result.txt').write_text('ok', encoding='utf-8')\n",
        encoding="utf-8",
    )
    claim = tmp_path / "claim.yml"
    claim.write_text(
        """apiVersion: reprocert.dev/v1alpha1
kind: ReproducibilityClaim
metadata: {id: policy-test}
spec:
  command: [python, produce.py]
  evidence: [result.txt]
  checks:
    - id: output
      source: {type: text, path: result.txt}
      op: eq
      expected: ok
""",
        encoding="utf-8",
    )
    policy_path = tmp_path / "policy.yml"
    policy_path.write_text(
        """apiVersion: reprocert.dev/policy/v1alpha1
kind: ReproCertPolicy
metadata: {id: container-required}
spec:
  allowed_verdicts: [PASS]
  require_container: true
""",
        encoding="utf-8",
    )

    certificate = run_claim(load_claim(claim))
    result = evaluate_policy(certificate, load_policy(policy_path))

    assert certificate["verdict"] == "PASS"
    assert result["status"] == "FAIL"
    assert result["certificate"]["verdict"] == "PASS"
    assert len(result["integrity"]["result_sha256"]) == 64


def test_pytest_adapter_passes_and_verifies(tmp_path: Path) -> None:
    (tmp_path / "test_sample.py").write_text(
        "def test_ok():\n    assert 2 + 2 == 4\n",
        encoding="utf-8",
    )
    certificate, generated_claim = run_pytest_adapter(
        working_directory=tmp_path,
        pytest_args=["-q"],
    )

    assert certificate["verdict"] == "PASS"
    assert certificate["metadata"]["adapter"] == "pytest-native"
    assert verify_certificate(
        certificate,
        claim_path=generated_claim,
        evidence_root=tmp_path,
    )["status"] == "PASS"


def test_pytest_test_failure_is_fail_not_error(tmp_path: Path) -> None:
    (tmp_path / "test_sample.py").write_text(
        "def test_bad():\n    assert False\n",
        encoding="utf-8",
    )
    certificate, _ = run_pytest_adapter(
        working_directory=tmp_path,
        pytest_args=["-q"],
    )

    assert certificate["run"]["exit_code"] == 1
    assert certificate["verdict"] == "FAIL"
    assert any(
        check["id"] == "pytest-failures"
        and check["status"] == "FAIL"
        for check in certificate["checks"]
    )
