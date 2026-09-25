from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .util import canonical_json_bytes, sha256_bytes
from .verification import verify_certificate

POLICY_API_VERSION = "reprocert.dev/policy/v1alpha1"
POLICY_KIND = "ReproCertPolicy"


class PolicyError(ValueError):
    pass


@dataclass(frozen=True)
class Policy:
    raw: dict[str, Any]
    path: Path

    @property
    def policy_id(self) -> str:
        return str(self.raw["metadata"]["id"])

    @property
    def spec(self) -> dict[str, Any]:
        return self.raw["spec"]

    @property
    def digest(self) -> str:
        return sha256_bytes(canonical_json_bytes(self.raw))


def load_policy(path: str | Path) -> Policy:
    policy_path = Path(path).resolve()
    try:
        text = policy_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PolicyError(f"Cannot read policy file: {exc}") from exc

    try:
        raw = (
            json.loads(text)
            if policy_path.suffix.lower() == ".json"
            else yaml.safe_load(text)
        )
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise PolicyError(f"Invalid policy syntax: {exc}") from exc

    if not isinstance(raw, dict):
        raise PolicyError("Policy root must be an object")
    validate_policy(raw)
    return Policy(raw=raw, path=policy_path)


def validate_policy(raw: dict[str, Any]) -> None:
    if raw.get("apiVersion") != POLICY_API_VERSION:
        raise PolicyError(f"apiVersion must be {POLICY_API_VERSION!r}")
    if raw.get("kind") != POLICY_KIND:
        raise PolicyError(f"kind must be {POLICY_KIND!r}")

    metadata = raw.get("metadata")
    spec = raw.get("spec")
    if not isinstance(metadata, dict) or not metadata.get("id"):
        raise PolicyError("metadata.id is required")
    if not isinstance(spec, dict):
        raise PolicyError("spec must be an object")

    allowed = spec.get("allowed_verdicts", ["PASS"])
    if (
        not isinstance(allowed, list)
        or not allowed
        or any(
            verdict not in {"PASS", "FAIL", "INCONCLUSIVE", "ERROR"}
            for verdict in allowed
        )
    ):
        raise PolicyError(
            "spec.allowed_verdicts must be a non-empty verdict list"
        )

    for key in ("require_ci", "require_git_clean", "require_container"):
        if key in spec and not isinstance(spec[key], bool):
            raise PolicyError(f"spec.{key} must be boolean")

    for key in ("min_evidence_files", "max_diagnostics"):
        if key in spec and (
            not isinstance(spec[key], int)
            or isinstance(spec[key], bool)
            or spec[key] < 0
        ):
            raise PolicyError(f"spec.{key} must be a non-negative integer")

    required = spec.get("required_check_ids", [])
    if not isinstance(required, list) or any(
        not isinstance(item, str) or not item for item in required
    ):
        raise PolicyError(
            "spec.required_check_ids must be an array of strings"
        )


def evaluate_policy(
    certificate: dict[str, Any],
    policy: Policy,
) -> dict[str, Any]:
    rules: list[dict[str, Any]] = []
    spec = policy.spec

    verification = verify_certificate(certificate)
    _rule(
        rules,
        "certificate_integrity",
        verification["status"] == "PASS",
        "PASS",
        verification["status"],
    )

    allowed = spec.get("allowed_verdicts", ["PASS"])
    _rule(
        rules,
        "allowed_verdicts",
        certificate.get("verdict") in allowed,
        allowed,
        certificate.get("verdict"),
    )

    if spec.get("require_ci") is True:
        observed = bool(
            certificate.get("environment", {})
            .get("ci", {})
            .get("github_actions")
        )
        _rule(rules, "require_ci", observed, True, observed)

    if spec.get("require_git_clean") is True:
        observed = (
            certificate.get("environment", {})
            .get("git", {})
            .get("dirty")
        )
        _rule(
            rules,
            "require_git_clean",
            observed is False,
            False,
            observed,
        )

    if "min_evidence_files" in spec:
        observed = len(certificate.get("evidence", []))
        expected = spec["min_evidence_files"]
        _rule(
            rules,
            "min_evidence_files",
            observed >= expected,
            expected,
            observed,
        )

    if "max_diagnostics" in spec:
        observed = len(certificate.get("diagnostics", []))
        expected = spec["max_diagnostics"]
        _rule(
            rules,
            "max_diagnostics",
            observed <= expected,
            expected,
            observed,
        )

    required_ids = spec.get("required_check_ids", [])
    if required_ids:
        observed_ids = {
            str(check.get("id"))
            for check in certificate.get("checks", [])
            if check.get("id") is not None
        }
        missing = sorted(set(required_ids) - observed_ids)
        _rule(
            rules,
            "required_check_ids",
            not missing,
            sorted(required_ids),
            sorted(observed_ids),
        )

    if spec.get("require_container") is True:
        observed = isinstance(
            certificate.get("run", {}).get("container"),
            dict,
        )
        _rule(
            rules,
            "require_container",
            observed,
            True,
            observed,
        )

    status = (
        "PASS"
        if all(rule["status"] == "PASS" for rule in rules)
        else "FAIL"
    )
    result: dict[str, Any] = {
        "apiVersion": "reprocert.dev/policy-result/v1alpha1",
        "kind": "ReproCertPolicyResult",
        "metadata": {
            "policy_id": policy.policy_id,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
        },
        "policy": {
            "path": policy.path.name,
            "sha256": policy.digest,
        },
        "certificate": {
            "sha256": certificate.get("integrity", {}).get(
                "certificate_sha256"
            ),
            "verdict": certificate.get("verdict"),
        },
        "rules": rules,
        "status": status,
        "trustBoundary": (
            "Policy evaluation is an additional acceptance layer. It does "
            "not rewrite the underlying ReproCert verdict or establish "
            "producer authenticity, evidence-source truth, or scientific "
            "validity."
        ),
    }
    result["integrity"] = {
        "algorithm": "sha256",
        "canonicalization": "JSON_SORTED_KEYS_UTF8_V1",
    }
    result["integrity"]["result_sha256"] = _result_digest(result)
    return result


def _rule(
    rules: list[dict[str, Any]],
    rule_id: str,
    passed: bool,
    expected: Any,
    observed: Any,
) -> None:
    rules.append(
        {
            "id": rule_id,
            "status": "PASS" if passed else "FAIL",
            "expected": expected,
            "observed": observed,
        }
    )


def _result_digest(result: dict[str, Any]) -> str:
    material = json.loads(json.dumps(result))
    material.get("integrity", {}).pop("result_sha256", None)
    return sha256_bytes(canonical_json_bytes(material))
