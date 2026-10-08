from __future__ import annotations

import copy
import tomllib
from pathlib import Path

from reprocert.certificate import seal_certificate
from reprocert.claim import load_claim
from reprocert.init_project import initialize_project
from reprocert.policy import evaluate_policy, load_policy
from reprocert.runner import run_claim
from reprocert.verification import verify_certificate


def _write_claim(path: Path, api_version: str) -> Path:
    path.write_text(
        f"""apiVersion: {api_version}
kind: ReproducibilityClaim
metadata:
  id: transition-boundary
spec:
  command: [python, -c, "print('transition-ok')"]
  checks:
    - id: marker
      source: {{type: stdout}}
      op: contains
      expected: transition-ok
""",
        encoding="utf-8",
    )
    return path


def test_alpha_to_stable_version_flip_changes_identity_and_breaks_binding(
    tmp_path: Path,
) -> None:
    alpha_path = _write_claim(tmp_path / "claim.yml", "reprocert.dev/v1alpha1")
    alpha_claim = load_claim(alpha_path)
    alpha_certificate = run_claim(alpha_claim)
    alpha_digest = alpha_claim.digest

    text = alpha_path.read_text(encoding="utf-8")
    alpha_path.write_text(
        text.replace("reprocert.dev/v1alpha1", "reprocert.dev/v1", 1),
        encoding="utf-8",
    )
    stable_claim = load_claim(alpha_path)

    assert stable_claim.digest != alpha_digest
    verification = verify_certificate(alpha_certificate, claim_path=alpha_path)
    assert verification["status"] == "FAIL"
    claim_check = next(
        item for item in verification["checks"] if item["name"] == "claim_digest"
    )
    assert claim_check["status"] == "FAIL"


def test_resealed_certificate_never_becomes_producer_authentication(
    tmp_path: Path,
) -> None:
    claim_path = _write_claim(tmp_path / "claim.yml", "reprocert.dev/v1")
    certificate = run_claim(load_claim(claim_path))

    resealed = copy.deepcopy(certificate)
    resealed["metadata"]["tool_version"] = "synthetic-resealed-producer"
    seal_certificate(resealed)

    verification = verify_certificate(resealed, claim_path=claim_path)
    assert verification["status"] == "PASS"
    boundary = verification["trust_boundary"].lower()
    assert "does not authenticate the producer" in boundary
    assert "signed" in boundary


def test_policy_pass_cannot_launder_resealed_certificate_into_authentication(
    tmp_path: Path,
) -> None:
    claim_path = _write_claim(tmp_path / "claim.yml", "reprocert.dev/v1")
    certificate = run_claim(load_claim(claim_path))
    seal_certificate(certificate)

    policy_path = tmp_path / "policy.yml"
    policy_path.write_text(
        """apiVersion: reprocert.dev/policy/v1
kind: ReproCertPolicy
metadata: {id: transition-policy}
spec:
  allowed_verdicts: [PASS]
""",
        encoding="utf-8",
    )
    result = evaluate_policy(certificate, load_policy(policy_path))

    assert result["status"] == "PASS"
    boundary = result["trustBoundary"].lower()
    assert "does not rewrite" in boundary
    assert "producer authenticity" in boundary


def test_rc_identity_cannot_satisfy_final_release_tag() -> None:
    data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    version = data["project"]["version"]

    assert version == "1.0.0rc1"
    assert f"v{version}" == "v1.0.0rc1"
    assert f"v{version}" != "v1.0.0"


def test_generated_stable_workflow_never_downgrades_to_alpha_channel(
    tmp_path: Path,
) -> None:
    initialize_project(tmp_path, profile="command", github_actions=True)
    workflow = (
        tmp_path / ".github" / "workflows" / "reprocert.yml"
    ).read_text(encoding="utf-8")

    assert "AETHERXGLOBAL/reprocert@v1" in workflow
    assert "AETHERXGLOBAL/reprocert@v0.2" not in workflow


def test_release_workflow_remains_bound_to_tag_version_and_current_main() -> None:
    workflow = Path(".github/workflows/release.yml").read_text(encoding="utf-8")

    required = [
        "types: [published]",
        "RELEASE_TAG: ${{ github.event.release.tag_name }}",
        'expected = f"v{version}"',
        'git fetch --no-tags origin main',
        'test "$released" = "$current_main"',
        "id-token: write",
    ]
    for marker in required:
        assert marker in workflow
