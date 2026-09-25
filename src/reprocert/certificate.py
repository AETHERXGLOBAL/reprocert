from __future__ import annotations

import copy
from typing import Any

from .util import canonical_json_bytes, sha256_bytes

CERT_API_VERSION = "reprocert.dev/certificate/v1alpha1"
CERT_KIND = "ReproCertCertificate"
CANONICALIZATION = "JSON_SORTED_KEYS_UTF8_V1"


def compute_certificate_digest(certificate: dict[str, Any]) -> str:
    material = copy.deepcopy(certificate)
    integrity = material.setdefault("integrity", {})
    integrity.pop("certificate_sha256", None)
    return sha256_bytes(canonical_json_bytes(material))


def seal_certificate(certificate: dict[str, Any]) -> dict[str, Any]:
    certificate.setdefault("integrity", {})
    certificate["integrity"].update(
        {
            "algorithm": "sha256",
            "canonicalization": CANONICALIZATION,
        }
    )
    certificate["integrity"]["certificate_sha256"] = compute_certificate_digest(certificate)
    return certificate
