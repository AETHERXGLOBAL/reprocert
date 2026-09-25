from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET


class JUnitError(ValueError):
    pass


def read_junit_metrics(path: str | Path) -> dict[str, int | float]:
    report_path = Path(path)
    data = report_path.read_bytes()
    upper = data.upper()
    if b"<!DOCTYPE" in upper or b"<!ENTITY" in upper:
        raise JUnitError("DTD/entity declarations are not accepted in JUnit evidence")

    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise JUnitError(f"Invalid JUnit XML: {exc}") from exc

    root_name = _local_name(root.tag)
    if root_name == "testsuite":
        suites = [root]
    elif root_name == "testsuites":
        suites = [child for child in root if _local_name(child.tag) == "testsuite"]
    else:
        raise JUnitError("JUnit root must be <testsuite> or <testsuites>")

    if not suites:
        raise JUnitError("JUnit document contains no test suites")

    totals: dict[str, int | float] = {
        "tests": 0,
        "failures": 0,
        "errors": 0,
        "skipped": 0,
        "passed": 0,
        "time_seconds": 0.0,
    }

    for suite in suites:
        tests = _int_attr_or_count(suite, "tests", "testcase")
        failures = _int_attr_or_count(suite, "failures", "failure")
        errors = _int_attr_or_count(suite, "errors", "error")
        skipped = _int_attr_or_count(suite, "skipped", "skipped")
        time_seconds = _float_attr(suite, "time", 0.0)

        for name, value in (
            ("tests", tests),
            ("failures", failures),
            ("errors", errors),
            ("skipped", skipped),
        ):
            if value < 0:
                raise JUnitError(f"JUnit {name} cannot be negative")

        totals["tests"] = int(totals["tests"]) + tests
        totals["failures"] = int(totals["failures"]) + failures
        totals["errors"] = int(totals["errors"]) + errors
        totals["skipped"] = int(totals["skipped"]) + skipped
        totals["time_seconds"] = float(totals["time_seconds"]) + time_seconds

    passed = (
        int(totals["tests"])
        - int(totals["failures"])
        - int(totals["errors"])
        - int(totals["skipped"])
    )
    totals["passed"] = max(0, passed)
    totals["time_seconds"] = round(float(totals["time_seconds"]), 6)
    return totals


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _int_attr_or_count(element: ET.Element, attr: str, descendant: str) -> int:
    raw = element.get(attr)
    if raw is not None:
        try:
            return int(raw)
        except ValueError as exc:
            raise JUnitError(f"JUnit attribute {attr!r} must be an integer") from exc

    if attr == "tests":
        return sum(1 for child in element.iter() if _local_name(child.tag) == descendant)

    count = 0
    for case in (child for child in element.iter() if _local_name(child.tag) == "testcase"):
        if any(_local_name(child.tag) == descendant for child in case):
            count += 1
    return count


def _float_attr(element: ET.Element, attr: str, default: float) -> float:
    raw = element.get(attr)
    if raw is None:
        return default
    try:
        value = float(raw)
    except ValueError as exc:
        raise JUnitError(f"JUnit attribute {attr!r} must be numeric") from exc
    if value < 0:
        raise JUnitError(f"JUnit attribute {attr!r} cannot be negative")
    return value
