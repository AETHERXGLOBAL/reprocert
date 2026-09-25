from __future__ import annotations

import json
from pathlib import Path

import pytest

from reprocert.attestation import PREDICATE_TYPE, predicate_from_certificate
from reprocert.claim import ClaimError, load_claim
from reprocert.junit import JUnitError, read_junit_metrics
from reprocert.runner import run_claim
from reprocert.suite import SuiteError, load_suite, run_suite
from reprocert.verification import verify_certificate


def _write_claim(
    directory: Path,
    name: str,
    observed: int,
    expected: int,
) -> Path:
    script = directory / f"{name}.py"
    result = directory / f"{name}.json"
    script.write_text(
        "import json\n"
        f"json.dump({{'value': {observed}}}, "
        f"open({result.name!r}, 'w'))\n",
        encoding="utf-8",
    )
    claim = directory / f"{name}.yml"
    claim.write_text(
        f"""apiVersion: reprocert.dev/v1alpha1
kind: ReproducibilityClaim
metadata:
  id: {name}
spec:
  command: [python, {script.name}]
  evidence: [{result.name}]
  checks:
    - id: value-under-limit
      source:
        type: json
        path: {result.name}
        pointer: /value
      op: lt
      expected: {expected}
""",
        encoding="utf-8",
    )
    return claim


def test_junit_metrics_are_aggregated(tmp_path: Path) -> None:
    report = tmp_path / "junit.xml"
    report.write_text(
        """<testsuites>
  <testsuite tests="3" failures="1" errors="0" skipped="1" time="0.5">
    <testcase name="a"/>
    <testcase name="b"><failure/></testcase>
    <testcase name="c"><skipped/></testcase>
  </testsuite>
  <testsuite tests="2" failures="0" errors="0" skipped="0" time="0.25">
    <testcase name="d"/>
    <testcase name="e"/>
  </testsuite>
</testsuites>""",
        encoding="utf-8",
    )
    metrics = read_junit_metrics(report)
    assert metrics == {
        "tests": 5,
        "failures": 1,
        "errors": 0,
        "skipped": 1,
        "passed": 3,
        "time_seconds": 0.75,
    }


def test_junit_dtd_and_entities_are_rejected(tmp_path: Path) -> None:
    report = tmp_path / "junit.xml"
    report.write_text(
        '<!DOCTYPE x [<!ENTITY e "boom">]><testsuite tests="0"/>',
        encoding="utf-8",
    )
    with pytest.raises(JUnitError):
        read_junit_metrics(report)


def test_junit_source_can_drive_a_claim(tmp_path: Path) -> None:
    (tmp_path / "make.py").write_text(
        "from pathlib import Path\n"
        "Path('junit.xml').write_text("
        "'<testsuite tests=\"3\" failures=\"0\" errors=\"0\" "
        "skipped=\"1\" time=\"0.1\"/>', encoding='utf-8')\n",
        encoding="utf-8",
    )
    claim = tmp_path / "claim.yml"
    claim.write_text(
        """apiVersion: reprocert.dev/v1alpha1
kind: ReproducibilityClaim
metadata: {id: junit-gate}
spec:
  command: [python, make.py]
  evidence: [junit.xml]
  checks:
    - id: no-failures
      source: {type: junit, path: junit.xml, metric: failures}
      op: eq
      expected: 0
    - id: two-passed
      source: {type: junit, path: junit.xml, metric: passed}
      op: eq
      expected: 2
""",
        encoding="utf-8",
    )
    certificate = run_claim(load_claim(claim))
    assert certificate["verdict"] == "PASS"
    assert certificate["checks"][1]["observed"] == 2


def test_invalid_junit_metric_is_rejected(tmp_path: Path) -> None:
    claim = tmp_path / "claim.yml"
    claim.write_text(
        """apiVersion: reprocert.dev/v1alpha1
kind: ReproducibilityClaim
metadata: {id: invalid}
spec:
  command: [python, x.py]
  checks:
    - id: bad
      source: {type: junit, path: junit.xml, metric: secrets}
      op: eq
      expected: 0
""",
        encoding="utf-8",
    )
    with pytest.raises(ClaimError):
        load_claim(claim)


def test_suite_runs_multiple_claims_and_preserves_fail(tmp_path: Path) -> None:
    _write_claim(tmp_path, "pass-claim", 2, 10)
    _write_claim(tmp_path, "fail-claim", 20, 10)
    suite_path = tmp_path / "suite.yml"
    suite_path.write_text(
        """apiVersion: reprocert.dev/suite/v1alpha1
kind: ReproCertSuite
metadata:
  id: mixed-suite
spec:
  claims:
    - pass-claim.yml
    - fail-claim.yml
""",
        encoding="utf-8",
    )

    report, certificates = run_suite(load_suite(suite_path))
    assert report["verdict"] == "FAIL"
    assert len(certificates) == 2
    assert len(report["integrity"]["report_sha256"]) == 64
    assert [item["verdict"] for item in report["claims"]] == ["PASS", "FAIL"]


def test_suite_path_traversal_is_rejected(tmp_path: Path) -> None:
    suite_path = tmp_path / "suite.yml"
    suite_path.write_text(
        """apiVersion: reprocert.dev/suite/v1alpha1
kind: ReproCertSuite
metadata: {id: escape}
spec:
  claims: [../claim.yml]
""",
        encoding="utf-8",
    )
    with pytest.raises(SuiteError):
        load_suite(suite_path)


def test_attestation_predicate_is_privacy_minimized(tmp_path: Path) -> None:
    (tmp_path / "produce.py").write_text(
        "from pathlib import Path\n"
        "Path('result.txt').write_text('ok', encoding='utf-8')\n"
        "print('DO-NOT-COPY-STDOUT')\n",
        encoding="utf-8",
    )
    claim_path = tmp_path / "claim.yml"
    claim_path.write_text(
        """apiVersion: reprocert.dev/v1alpha1
kind: ReproducibilityClaim
metadata: {id: predicate-test}
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
    certificate = run_claim(load_claim(claim_path))
    predicate = predicate_from_certificate(certificate)
    encoded = json.dumps(predicate)

    assert predicate["predicateType"] == PREDICATE_TYPE
    assert predicate["result"]["verdict"] == "PASS"
    assert certificate["integrity"]["certificate_sha256"] in encoded
    assert "DO-NOT-COPY-STDOUT" not in encoded
    assert "produce.py" not in encoded
    assert verify_certificate(
        certificate,
        claim_path=claim_path,
        evidence_root=tmp_path,
    )["status"] == "PASS"
