from __future__ import annotations

import copy
import json
from pathlib import Path

from reprocert.certificate import (
    CERT_API_VERSION,
    LEGACY_CERT_API_VERSION,
    seal_certificate,
)
from reprocert.claim import (
    CLAIM_API_VERSION,
    LEGACY_CLAIM_API_VERSION,
    load_claim,
)
from reprocert.init_project import initialize_project
from reprocert.policy import POLICY_API_VERSION, LEGACY_POLICY_API_VERSION, load_policy
from reprocert.runner import run_claim
from reprocert.suite import SUITE_API_VERSION, LEGACY_SUITE_API_VERSION, load_suite
from reprocert.verification import load_certificate, verify_certificate


def _claim_text(api_version: str) -> str:
    return f"""apiVersion: {api_version}
kind: ReproducibilityClaim
metadata:
  id: compatibility
  title: Compatibility fixture
spec:
  command: [python, -c, "print('ok')"]
  checks:
    - id: marker
      source: {{type: stdout}}
      op: contains
      expected: ok
"""


def test_stable_claim_emits_stable_certificate(tmp_path: Path) -> None:
    claim_path = tmp_path / "claim.yml"
    claim_path.write_text(_claim_text(CLAIM_API_VERSION), encoding="utf-8")

    claim = load_claim(claim_path)
    certificate = run_claim(claim)

    assert claim.raw["apiVersion"] == "reprocert.dev/v1"
    assert certificate["apiVersion"] == "reprocert.dev/certificate/v1"
    assert verify_certificate(certificate, claim_path=claim_path)["status"] == "PASS"


def test_v1_reads_legacy_alpha_claim_without_rewriting_it(tmp_path: Path) -> None:
    claim_path = tmp_path / "legacy-claim.yml"
    claim_path.write_text(_claim_text(LEGACY_CLAIM_API_VERSION), encoding="utf-8")

    claim = load_claim(claim_path)
    original_digest = claim.digest
    certificate = run_claim(claim)

    assert claim.raw["apiVersion"] == "reprocert.dev/v1alpha1"
    assert claim.digest == original_digest
    assert certificate["claim"]["sha256"] == original_digest
    assert certificate["apiVersion"] == CERT_API_VERSION


def test_v1_verifier_accepts_legacy_alpha_certificate(tmp_path: Path) -> None:
    claim_path = tmp_path / "legacy-claim.yml"
    claim_path.write_text(_claim_text(LEGACY_CLAIM_API_VERSION), encoding="utf-8")
    claim = load_claim(claim_path)

    certificate = run_claim(claim)
    legacy = copy.deepcopy(certificate)
    legacy["apiVersion"] = LEGACY_CERT_API_VERSION
    seal_certificate(legacy)

    cert_path = tmp_path / "legacy-certificate.json"
    cert_path.write_text(json.dumps(legacy, indent=2) + "\n", encoding="utf-8")

    loaded = load_certificate(cert_path)
    assert loaded["apiVersion"] == "reprocert.dev/certificate/v1alpha1"
    assert verify_certificate(
        loaded,
        claim_path=claim_path,
        evidence_root=tmp_path,
    )["status"] == "PASS"


def test_stable_and_legacy_policy_versions_are_accepted(tmp_path: Path) -> None:
    for api_version in (POLICY_API_VERSION, LEGACY_POLICY_API_VERSION):
        policy_path = tmp_path / f"policy-{api_version.rsplit('/', 1)[-1]}.yml"
        policy_path.write_text(
            f"""apiVersion: {api_version}
kind: ReproCertPolicy
metadata:
  id: policy
spec:
  allowed_verdicts: [PASS]
""",
            encoding="utf-8",
        )
        policy = load_policy(policy_path)
        assert policy.raw["apiVersion"] == api_version


def test_stable_and_legacy_suite_versions_are_accepted(tmp_path: Path) -> None:
    claim_path = tmp_path / "claim.yml"
    claim_path.write_text(_claim_text(CLAIM_API_VERSION), encoding="utf-8")

    for api_version in (SUITE_API_VERSION, LEGACY_SUITE_API_VERSION):
        suite_path = tmp_path / f"suite-{api_version.rsplit('/', 1)[-1]}.yml"
        suite_path.write_text(
            f"""apiVersion: {api_version}
kind: ReproCertSuite
metadata:
  id: suite
spec:
  claims: [claim.yml]
""",
            encoding="utf-8",
        )
        suite = load_suite(suite_path)
        assert suite.raw["apiVersion"] == api_version


def test_init_generates_stable_v1_contract(tmp_path: Path) -> None:
    initialize_project(tmp_path, profile="command", github_actions=True)

    claim = (tmp_path / "reprocert.yml").read_text(encoding="utf-8")
    workflow = (
        tmp_path / ".github" / "workflows" / "reprocert.yml"
    ).read_text(encoding="utf-8")

    assert "apiVersion: reprocert.dev/v1" in claim
    assert "reprocert.dev/v1alpha1" not in claim
    assert "AETHERXGLOBAL/reprocert@v1" in workflow
    assert "AETHERXGLOBAL/reprocert@v0.2" not in workflow


def test_stable_schema_files_match_stable_api_versions() -> None:
    expected = {
        "claim-v1.schema.json": CLAIM_API_VERSION,
        "certificate-v1.schema.json": CERT_API_VERSION,
        "policy-v1.schema.json": POLICY_API_VERSION,
        "suite-v1.schema.json": SUITE_API_VERSION,
    }
    for name, api_version in expected.items():
        schema = json.loads((Path("schemas") / name).read_text(encoding="utf-8"))
        assert schema["properties"]["apiVersion"]["const"] == api_version
