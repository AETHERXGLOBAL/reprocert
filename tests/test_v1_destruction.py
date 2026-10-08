from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from reprocert.attestation import predicate_from_certificate
from reprocert.certificate import seal_certificate
from reprocert.claim import ClaimError, load_claim
from reprocert.policy import PolicyError, evaluate_policy, load_policy
from reprocert.runner import run_claim
from reprocert.suite import SuiteError, load_suite, run_suite
from reprocert.verification import load_certificate, verify_certificate


def _write_claim(path: Path, *, api_version: str = "reprocert.dev/v1", expected: str = "ok") -> Path:
    path.write_text(
        f"""apiVersion: {api_version}
kind: ReproducibilityClaim
metadata:
  id: destruction
spec:
  command: [python, -c, "print('ok')"]
  checks:
    - id: marker
      source: {{type: stdout}}
      op: contains
      expected: {expected}
""",
        encoding="utf-8",
    )
    return path


@pytest.mark.parametrize(
    "api_version",
    [
        "reprocert.dev/v1beta1",
        "reprocert.dev/v1alpha2",
        "reprocert.dev/v2",
        "reprocert.dev/V1",
        "reprocert.dev/v1/",
    ],
)
def test_claim_near_miss_versions_are_rejected(tmp_path: Path, api_version: str) -> None:
    with pytest.raises(ClaimError):
        load_claim(_write_claim(tmp_path / "claim.yml", api_version=api_version))


def test_unknown_resealed_certificate_version_is_rejected(tmp_path: Path) -> None:
    claim_path = _write_claim(tmp_path / "claim.yml")
    certificate = run_claim(load_claim(claim_path))

    forged = copy.deepcopy(certificate)
    forged["apiVersion"] = "reprocert.dev/certificate/v2"
    seal_certificate(forged)
    cert_path = tmp_path / "forged.json"
    cert_path.write_text(json.dumps(forged) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported certificate format"):
        load_certificate(cert_path)


def test_wrong_claim_identity_cannot_verify(tmp_path: Path) -> None:
    claim_path = _write_claim(tmp_path / "claim.yml")
    wrong_path = _write_claim(tmp_path / "wrong.yml", expected="different")
    certificate = run_claim(load_claim(claim_path))

    result = verify_certificate(certificate, claim_path=wrong_path)
    assert result["status"] == "FAIL"
    claim_check = next(check for check in result["checks"] if check["name"] == "claim_digest")
    assert claim_check["status"] == "FAIL"


def test_valid_digest_cannot_launder_evidence_path_escape(tmp_path: Path) -> None:
    claim_path = _write_claim(tmp_path / "claim.yml")
    certificate = run_claim(load_claim(claim_path))

    escaped = copy.deepcopy(certificate)
    escaped["evidence"] = [
        {
            "path": "../outside.txt",
            "sha256": "0" * 64,
            "size": 1,
        }
    ]
    seal_certificate(escaped)

    result = verify_certificate(escaped, evidence_root=tmp_path)
    assert result["status"] == "FAIL"
    evidence_check = next(
        check for check in result["checks"] if check["name"] == "evidence:../outside.txt"
    )
    assert evidence_check["observed"] == "path escaped root"


def test_policy_pass_never_rewrites_failed_certificate_verdict(tmp_path: Path) -> None:
    claim_path = _write_claim(tmp_path / "claim.yml", expected="not-present")
    certificate = run_claim(load_claim(claim_path))
    assert certificate["verdict"] == "FAIL"

    policy_path = tmp_path / "policy.yml"
    policy_path.write_text(
        """apiVersion: reprocert.dev/policy/v1
kind: ReproCertPolicy
metadata: {id: preserve-verdict}
spec:
  allowed_verdicts: [FAIL]
""",
        encoding="utf-8",
    )
    result = evaluate_policy(certificate, load_policy(policy_path))

    assert result["status"] == "PASS"
    assert result["certificate"]["verdict"] == "FAIL"
    assert certificate["verdict"] == "FAIL"


@pytest.mark.parametrize(
    "api_version",
    [
        "reprocert.dev/policy/v1beta1",
        "reprocert.dev/policy/v2",
    ],
)
def test_policy_near_miss_versions_are_rejected(tmp_path: Path, api_version: str) -> None:
    policy_path = tmp_path / "policy.yml"
    policy_path.write_text(
        f"""apiVersion: {api_version}
kind: ReproCertPolicy
metadata: {{id: bad-policy}}
spec: {{}}
""",
        encoding="utf-8",
    )
    with pytest.raises(PolicyError):
        load_policy(policy_path)


@pytest.mark.parametrize(
    "api_version",
    [
        "reprocert.dev/suite/v1beta1",
        "reprocert.dev/suite/v2",
    ],
)
def test_suite_near_miss_versions_are_rejected(tmp_path: Path, api_version: str) -> None:
    suite_path = tmp_path / "suite.yml"
    suite_path.write_text(
        f"""apiVersion: {api_version}
kind: ReproCertSuite
metadata: {{id: bad-suite}}
spec:
  claims: [claim.yml]
""",
        encoding="utf-8",
    )
    with pytest.raises(SuiteError):
        load_suite(suite_path)


def test_stable_suite_can_execute_legacy_alpha_claim(tmp_path: Path) -> None:
    _write_claim(
        tmp_path / "legacy.yml",
        api_version="reprocert.dev/v1alpha1",
    )
    suite_path = tmp_path / "suite.yml"
    suite_path.write_text(
        """apiVersion: reprocert.dev/suite/v1
kind: ReproCertSuite
metadata: {id: mixed}
spec:
  claims: [legacy.yml]
""",
        encoding="utf-8",
    )

    report, certificates = run_suite(load_suite(suite_path))
    assert report["apiVersion"] == "reprocert.dev/suite-report/v1"
    assert report["verdict"] == "PASS"
    assert certificates[0][1]["apiVersion"] == "reprocert.dev/certificate/v1"


def test_integrity_verification_does_not_claim_producer_authentication(tmp_path: Path) -> None:
    claim_path = _write_claim(tmp_path / "claim.yml")
    certificate = run_claim(load_claim(claim_path))

    verification = verify_certificate(certificate)
    predicate = predicate_from_certificate(certificate)

    assert verification["status"] == "PASS"
    assert "does not authenticate the producer" in verification["trust_boundary"].lower()
    assert "does not establish" in predicate["trustBoundary"].lower()
    assert "scientific validity" in predicate["trustBoundary"].lower()
