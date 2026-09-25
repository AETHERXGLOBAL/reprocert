from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .attestation import PREDICATE_TYPE, predicate_from_certificate
from .claim import ClaimError, load_claim
from .runner import EvidenceResolutionError, run_claim
from .suite import SuiteError, load_suite, run_suite
from .verification import load_certificate, verify_certificate


EXIT_BY_VERDICT = {
    "PASS": 0,
    "FAIL": 1,
    "INCONCLUSIVE": 3,
    "ERROR": 4,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="reprocert",
        description="Claim-to-evidence reproducibility certificates",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("run", help="Run one claim and emit a certificate")
    p.add_argument("claim")
    p.add_argument(
        "--output",
        "-o",
        default="reprocert-certificate.json",
    )
    p.add_argument("--json", action="store_true")

    p = sub.add_parser(
        "suite",
        help="Run a suite of claims and emit an aggregate report",
    )
    p.add_argument("suite")
    p.add_argument(
        "--output",
        "-o",
        default="reprocert-suite-report.json",
    )
    p.add_argument(
        "--certificate-dir",
        default=".reprocert/certificates",
    )
    p.add_argument("--json", action="store_true")

    p = sub.add_parser(
        "verify",
        help="Verify certificate integrity and optional evidence",
    )
    p.add_argument("certificate")
    p.add_argument("--claim")
    p.add_argument("--evidence-root")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser(
        "predicate",
        help="Create a privacy-minimized custom attestation predicate",
    )
    p.add_argument("certificate")
    p.add_argument(
        "--output",
        "-o",
        default="reprocert-predicate.json",
    )
    p.add_argument("--json", action="store_true")

    p = sub.add_parser(
        "inspect",
        help="Show a certificate summary",
    )
    p.add_argument("certificate")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser(
        "diff",
        help="Compare two certificates",
    )
    p.add_argument("left")
    p.add_argument("right")
    p.add_argument("--json", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "run":
            return _run(args)
        if args.command == "suite":
            return _suite(args)
        if args.command == "verify":
            return _verify(args)
        if args.command == "predicate":
            return _predicate(args)
        if args.command == "inspect":
            return _inspect(args)
        if args.command == "diff":
            return _diff(args)
    except (
        ClaimError,
        SuiteError,
        EvidenceResolutionError,
        ValueError,
        OSError,
        json.JSONDecodeError,
    ) as exc:
        print(f"reprocert: {exc}", file=sys.stderr)
        return 2
    return 2


def _run(args: argparse.Namespace) -> int:
    claim = load_claim(args.claim)
    certificate = run_claim(claim)
    output = Path(args.output)
    _write_json(output, certificate)

    summary = {
        "claim_id": certificate["metadata"]["claim_id"],
        "verdict": certificate["verdict"],
        "certificate": str(output),
        "certificate_sha256": certificate["integrity"]["certificate_sha256"],
    }
    if args.json:
        print(json.dumps(summary, sort_keys=True))
    else:
        print(f"ReproCert verdict: {certificate['verdict']}")
        print(f"Certificate: {output}")
        print(f"Digest: {certificate['integrity']['certificate_sha256']}")

    return EXIT_BY_VERDICT.get(certificate["verdict"], 2)


def _suite(args: argparse.Namespace) -> int:
    suite = load_suite(args.suite)
    report, certificates = run_suite(suite)

    output = Path(args.output)
    certificate_dir = Path(args.certificate_dir)
    _write_json(output, report)
    certificate_dir.mkdir(parents=True, exist_ok=True)

    certificate_paths: list[str] = []
    for index, (_claim_path, certificate) in enumerate(certificates, start=1):
        claim_id = _safe_filename(str(certificate["metadata"]["claim_id"]))
        target = certificate_dir / f"{index:02d}-{claim_id}.json"
        _write_json(target, certificate)
        certificate_paths.append(str(target))

    summary = {
        "suite_id": report["metadata"]["suite_id"],
        "verdict": report["verdict"],
        "report": str(output),
        "report_sha256": report["integrity"]["report_sha256"],
        "certificates": certificate_paths,
    }

    if args.json:
        print(json.dumps(summary, sort_keys=True))
    else:
        print(f"ReproCert suite verdict: {report['verdict']}")
        print(f"Claims: {len(report['claims'])}")
        print(f"Report: {output}")
        print(f"Digest: {report['integrity']['report_sha256']}")

    return EXIT_BY_VERDICT.get(report["verdict"], 2)


def _verify(args: argparse.Namespace) -> int:
    result = verify_certificate(
        load_certificate(args.certificate),
        claim_path=args.claim,
        evidence_root=args.evidence_root,
    )
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(f"Certificate verification: {result['status']}")
        for check in result["checks"]:
            print(f"- {check['status']}: {check['name']}")
        print(result["trust_boundary"])
    return 0 if result["status"] == "PASS" else 1


def _predicate(args: argparse.Namespace) -> int:
    certificate = load_certificate(args.certificate)
    predicate = predicate_from_certificate(certificate)
    output = Path(args.output)
    _write_json(output, predicate)

    summary = {
        "predicate": str(output),
        "predicate_type": PREDICATE_TYPE,
        "certificate_sha256": certificate["integrity"]["certificate_sha256"],
        "verdict": certificate["verdict"],
    }
    if args.json:
        print(json.dumps(summary, sort_keys=True))
    else:
        print(f"Predicate: {output}")
        print(f"Predicate type: {PREDICATE_TYPE}")
        print(f"Certificate verdict: {certificate['verdict']}")
    return 0


def _inspect(args: argparse.Namespace) -> int:
    certificate = load_certificate(args.certificate)
    payload = {
        "claim_id": certificate["metadata"].get("claim_id"),
        "title": certificate["metadata"].get("title"),
        "verdict": certificate.get("verdict"),
        "commit": certificate.get("environment", {})
        .get("git", {})
        .get("commit"),
        "duration_ms": certificate.get("run", {}).get("duration_ms"),
        "evidence_files": len(certificate.get("evidence", [])),
        "certificate_sha256": certificate.get("integrity", {}).get(
            "certificate_sha256"
        ),
        "checks": [
            {
                "id": check.get("id"),
                "status": check.get("status"),
                "observed": check.get("observed"),
            }
            for check in certificate.get("checks", [])
        ],
    }

    if args.json:
        print(json.dumps(payload, sort_keys=True))
    else:
        print(f"Claim: {payload['claim_id']} — {payload['title']}")
        print(f"Verdict: {payload['verdict']}")
        print(f"Commit: {payload['commit']}")
        print(f"Duration: {payload['duration_ms']} ms")
        print(f"Evidence files: {payload['evidence_files']}")
        for check in payload["checks"]:
            print(
                f"- {check['status']}: {check['id']} "
                f"observed={check['observed']!r}"
            )
    return 0


def _diff(args: argparse.Namespace) -> int:
    payload = _diff_payload(
        load_certificate(args.left),
        load_certificate(args.right),
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True))
    else:
        print(f"Same claim: {payload['same_claim']}")
        print(
            f"Verdict: {payload['left_verdict']} -> "
            f"{payload['right_verdict']}"
        )
        for item in payload["changed_checks"]:
            print(
                f"- {item['id']}: {item['left']!r} -> "
                f"{item['right']!r}"
            )
    return 0


def _diff_payload(
    left: dict[str, Any],
    right: dict[str, Any],
) -> dict[str, Any]:
    left_checks = {
        check.get("id"): check for check in left.get("checks", [])
    }
    right_checks = {
        check.get("id"): check for check in right.get("checks", [])
    }
    changed: list[dict[str, Any]] = []

    for check_id in sorted(set(left_checks) | set(right_checks), key=str):
        left_value = left_checks.get(check_id, {}).get("observed")
        right_value = right_checks.get(check_id, {}).get("observed")
        if (
            left_value != right_value
            or left_checks.get(check_id, {}).get("status")
            != right_checks.get(check_id, {}).get("status")
        ):
            changed.append(
                {
                    "id": check_id,
                    "left": left_value,
                    "right": right_value,
                }
            )

    return {
        "same_claim": left.get("claim", {}).get("sha256")
        == right.get("claim", {}).get("sha256"),
        "left_verdict": left.get("verdict"),
        "right_verdict": right.get("verdict"),
        "changed_checks": changed,
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )


def _safe_filename(value: str) -> str:
    cleaned = "".join(
        char if char.isalnum() or char in {"-", "_", "."} else "-"
        for char in value
    )
    return cleaned.strip(".-") or "claim"


if __name__ == "__main__":
    raise SystemExit(main())
