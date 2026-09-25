from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class InitError(ValueError):
    pass


@dataclass(frozen=True)
class InitResult:
    profile: str
    created: tuple[str, ...]


def detect_profile(target: Path) -> str:
    if (target / "pytest.ini").exists() or (target / "conftest.py").exists():
        return "pytest"

    for name in ("pyproject.toml", "setup.cfg", "tox.ini"):
        path = target / name
        if path.is_file():
            try:
                if "pytest" in path.read_text(encoding="utf-8").lower():
                    return "pytest"
            except OSError:
                pass
    return "command"


def initialize_project(
    target: str | Path,
    *,
    profile: str | None = None,
    github_actions: bool = False,
    force: bool = False,
) -> InitResult:
    root = Path(target).resolve()
    if not root.exists() or not root.is_dir():
        raise InitError(f"Target directory does not exist: {root}")

    selected = profile or detect_profile(root)
    if selected not in {"pytest", "command", "benchmark"}:
        raise InitError(f"Unsupported init profile: {selected}")

    files: dict[Path, str] = {
        root / "reprocert.yml": _claim_template(selected),
        root / ".reprocert" / "README.md": _local_readme(selected),
    }
    if github_actions:
        files[root / ".github" / "workflows" / "reprocert.yml"] = _workflow_template(selected)

    conflicts = [path for path in files if path.exists() and not force]
    if conflicts:
        names = ", ".join(str(path.relative_to(root)) for path in conflicts)
        raise InitError(
            "Refusing to overwrite existing files: "
            f"{names}. Re-run with --force to replace them."
        )

    created: list[str] = []
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        created.append(str(path.relative_to(root)))

    return InitResult(profile=selected, created=tuple(created))


def _claim_template(profile: str) -> str:
    if profile == "pytest":
        return """apiVersion: reprocert.dev/v1alpha1
kind: ReproducibilityClaim
metadata:
  id: pytest-quality-gate
  title: Pytest suite completes without failures or errors
spec:
  command:
    - python
    - -m
    - pytest
    - -q
    - --junitxml
    - reprocert-junit.xml
  accepted_exit_codes: [0, 1]
  evidence:
    - reprocert-junit.xml
  checks:
    - id: pytest-failures
      source:
        type: junit
        path: reprocert-junit.xml
        metric: failures
      op: eq
      expected: 0
    - id: pytest-errors
      source:
        type: junit
        path: reprocert-junit.xml
        metric: errors
      op: eq
      expected: 0
"""

    if profile == "benchmark":
        return """apiVersion: reprocert.dev/v1alpha1
kind: ReproducibilityClaim
metadata:
  id: benchmark-threshold
  title: Benchmark median remains below the declared threshold
spec:
  command:
    - python
    - benchmark.py
  evidence:
    - benchmark.json
  checks:
    - id: median-threshold
      source:
        type: json
        path: benchmark.json
        pointer: /median_ms
      op: lt
      expected: 1000
"""

    return """apiVersion: reprocert.dev/v1alpha1
kind: ReproducibilityClaim
metadata:
  id: command-evidence
  title: Command emits the declared success marker
spec:
  command:
    - python
    - -c
    - "print('REPROCERT_OK')"
  checks:
    - id: success-marker
      source:
        type: stdout
      op: contains
      expected: REPROCERT_OK
"""


def _local_readme(profile: str) -> str:
    return f"""# ReproCert project configuration

Profile: {profile}

Run locally:

    reprocert doctor
    reprocert run reprocert.yml -o reprocert-certificate.json
    reprocert verify reprocert-certificate.json --claim reprocert.yml --evidence-root .

Edit reprocert.yml so the command and evidence describe your real project.
ReproCert is a verification layer; it does not replace your existing test,
benchmark, build, or research workflow.

Documentation:
https://github.com/AETHERXGLOBAL/reprocert
"""


def _workflow_template(profile: str) -> str:
    install_step = ""
    if profile == "pytest":
        install_step = """
      - name: Install project and test dependencies
        run: python -m pip install -e . pytest
"""
    return """name: ReproCert

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  reprocert:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v7

      - name: Set up Python
        uses: actions/setup-python@v7
        with:
          python-version: '3.13'

""" + install_step + """
      - name: Run ReproCert
        uses: AETHERXGLOBAL/reprocert@v0.2
        with:
          claim: reprocert.yml
          certificate: reprocert-certificate.json

      - name: Upload certificate
        uses: actions/upload-artifact@v7
        with:
          name: reprocert-certificate
          path: reprocert-certificate.json
          if-no-files-found: error
"""
