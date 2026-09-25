from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .claim import ClaimError, load_claim
from .runner import EvidenceResolutionError, run_claim
from .verification import load_certificate, verify_certificate


def build_parser() -> argparse.ArgumentParser:
    parser=argparse.ArgumentParser(prog="reprocert",description="Claim-to-evidence reproducibility certificates")
    parser.add_argument("--version",action="version",version=f"%(prog)s {__version__}")
    sub=parser.add_subparsers(dest="command",required=True)
    p=sub.add_parser("run",help="Run a claim and emit a certificate"); p.add_argument("claim"); p.add_argument("--output","-o",default="reprocert-certificate.json"); p.add_argument("--json",action="store_true")
    p=sub.add_parser("verify",help="Verify certificate integrity and optional evidence"); p.add_argument("certificate"); p.add_argument("--claim"); p.add_argument("--evidence-root"); p.add_argument("--json",action="store_true")
    p=sub.add_parser("inspect",help="Show a human-readable certificate summary"); p.add_argument("certificate")
    p=sub.add_parser("diff",help="Compare two certificates"); p.add_argument("left"); p.add_argument("right"); p.add_argument("--json",action="store_true")
    return parser


def main(argv: list[str] | None=None) -> int:
    args=build_parser().parse_args(argv)
    try:
        if args.command=="run": return _run(args)
        if args.command=="verify": return _verify(args)
        if args.command=="inspect": return _inspect(args)
        if args.command=="diff": return _diff(args)
    except (ClaimError,EvidenceResolutionError,ValueError,OSError,json.JSONDecodeError) as exc:
        print(f"reprocert: {exc}",file=sys.stderr); return 2
    return 2


def _run(args: argparse.Namespace) -> int:
    claim=load_claim(args.claim); cert=run_claim(claim); output=Path(args.output); output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(cert,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    summary={"claim_id":cert["metadata"]["claim_id"],"verdict":cert["verdict"],"certificate":str(output),"certificate_sha256":cert["integrity"]["certificate_sha256"]}
    if args.json: print(json.dumps(summary,sort_keys=True))
    else:
        print(f"ReproCert verdict: {cert['verdict']}"); print(f"Certificate: {output}"); print(f"Digest: {cert['integrity']['certificate_sha256']}")
    return {"PASS":0,"FAIL":1,"INCONCLUSIVE":3,"ERROR":4}.get(cert["verdict"],2)


def _verify(args: argparse.Namespace) -> int:
    result=verify_certificate(load_certificate(args.certificate),claim_path=args.claim,evidence_root=args.evidence_root)
    if args.json: print(json.dumps(result,sort_keys=True))
    else:
        print(f"Certificate verification: {result['status']}")
        for check in result["checks"]: print(f"- {check['status']}: {check['name']}")
        print(result["trust_boundary"])
    return 0 if result["status"]=="PASS" else 1


def _inspect(args: argparse.Namespace) -> int:
    cert=load_certificate(args.certificate)
    print(f"Claim: {cert['metadata'].get('claim_id')} — {cert['metadata'].get('title')}"); print(f"Verdict: {cert.get('verdict')}"); print(f"Commit: {cert.get('environment',{}).get('git',{}).get('commit')}"); print(f"Duration: {cert.get('run',{}).get('duration_ms')} ms"); print(f"Evidence files: {len(cert.get('evidence',[]))}")
    for check in cert.get("checks",[]): print(f"- {check.get('status')}: {check.get('id')} observed={check.get('observed')!r}")
    return 0


def _diff(args: argparse.Namespace) -> int:
    payload=_diff_payload(load_certificate(args.left),load_certificate(args.right))
    if args.json: print(json.dumps(payload,sort_keys=True))
    else:
        print(f"Same claim: {payload['same_claim']}"); print(f"Verdict: {payload['left_verdict']} -> {payload['right_verdict']}")
        for item in payload["changed_checks"]: print(f"- {item['id']}: {item['left']!r} -> {item['right']!r}")
    return 0


def _diff_payload(left: dict[str,Any],right: dict[str,Any]) -> dict[str,Any]:
    lchecks={c.get("id"):c for c in left.get("checks",[])}; rchecks={c.get("id"):c for c in right.get("checks",[])}; changed=[]
    for check_id in sorted(set(lchecks)|set(rchecks),key=str):
        lval=lchecks.get(check_id,{}).get("observed"); rval=rchecks.get(check_id,{}).get("observed")
        if lval!=rval or lchecks.get(check_id,{}).get("status")!=rchecks.get(check_id,{}).get("status"): changed.append({"id":check_id,"left":lval,"right":rval})
    return {"same_claim":left.get("claim",{}).get("sha256")==right.get("claim",{}).get("sha256"),"left_verdict":left.get("verdict"),"right_verdict":right.get("verdict"),"changed_checks":changed}

if __name__=="__main__": raise SystemExit(main())
