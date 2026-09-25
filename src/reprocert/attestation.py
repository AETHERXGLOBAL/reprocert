from __future__ import annotations

from typing import Any

PREDICATE_TYPE = (
    "https://raw.githubusercontent.com/AETHERXGLOBAL/reprocert/"
    "main/schemas/attestation-predicate-v1.schema.json"
)


def predicate_from_certificate(certificate: dict[str, Any]) -> dict[str, Any]:
    environment = certificate.get("environment", {})
    ci = environment.get("ci", {}) if isinstance(environment, dict) else {}
    git = environment.get("git", {}) if isinstance(environment, dict) else {}

    return {
        "schemaVersion": "1",
        "predicateType": PREDICATE_TYPE,
        "certificate": {
            "apiVersion": certificate.get("apiVersion"),
            "sha256": certificate.get("integrity", {}).get("certificate_sha256"),
        },
        "claim": {
            "id": certificate.get("metadata", {}).get("claim_id"),
            "sha256": certificate.get("claim", {}).get("sha256"),
        },
        "result": {
            "verdict": certificate.get("verdict"),
            "checks": [
                {"id": check.get("id"), "status": check.get("status")}
                for check in certificate.get("checks", [])
            ],
            "diagnostic_count": len(certificate.get("diagnostics", [])),
        },
        "evidence": [
            {
                "path": record.get("path"),
                "sha256": record.get("sha256"),
                "size": record.get("size"),
            }
            for record in certificate.get("evidence", [])
        ],
        "producerContext": {
            "repository": ci.get("repository"),
            "ref": ci.get("ref"),
            "workflow": ci.get("workflow"),
            "run_id": ci.get("run_id"),
            "commit": ci.get("sha") or git.get("commit"),
        },
        "tool": {
            "name": certificate.get("metadata", {}).get("tool"),
            "version": certificate.get("metadata", {}).get("tool_version"),
        },
        "trustBoundary": (
            "This predicate summarizes a ReproCert certificate for external "
            "attestation. Producer provenance does not establish evidence-source "
            "truth, benchmark representativeness, security certification, or "
            "scientific validity."
        ),
    }
