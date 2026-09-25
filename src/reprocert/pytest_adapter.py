from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from .claim import Claim, validate_claim
from .runner import run_claim


def run_pytest_adapter(
    *,
    working_directory: str | Path,
    pytest_args: list[str],
    junit_path: str = ".reprocert-pytest-junit.xml",
) -> tuple[dict[str, Any], Path]:
    workdir = Path(working_directory).resolve()
    if not workdir.is_dir():
        raise ValueError(f"pytest working directory does not exist: {workdir}")

    junit_rel = Path(junit_path)
    if junit_rel.is_absolute() or ".." in junit_rel.parts:
        raise ValueError("pytest JUnit path must stay inside the working directory")

    generated_claim = workdir / ".reprocert-pytest-claim.json"

    command = [
        sys.executable,
        "-m",
        "pytest",
        *pytest_args,
        "--junitxml",
        junit_path,
    ]

    raw: dict[str, Any] = {
        "apiVersion": "reprocert.dev/v1alpha1",
        "kind": "ReproducibilityClaim",
        "metadata": {
            "id": "pytest-native",
            "title": "Pytest native quality gate",
            "generated_by": "reprocert pytest",
        },
        "spec": {
            "command": command,
            "accepted_exit_codes": [0, 1],
            "evidence": [junit_path],
            "checks": [
                {
                    "id": "pytest-failures",
                    "source": {
                        "type": "junit",
                        "path": junit_path,
                        "metric": "failures",
                    },
                    "op": "eq",
                    "expected": 0,
                },
                {
                    "id": "pytest-errors",
                    "source": {
                        "type": "junit",
                        "path": junit_path,
                        "metric": "errors",
                    },
                    "op": "eq",
                    "expected": 0,
                },
            ],
        },
    }

    validate_claim(raw)
    generated_claim.write_text(
        json.dumps(raw, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    certificate = run_claim(Claim(raw=raw, path=generated_claim))
    certificate.setdefault("metadata", {})["adapter"] = "pytest-native"
    return certificate, generated_claim
