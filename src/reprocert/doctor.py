from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import __version__
from .claim import ClaimError, load_claim


@dataclass(frozen=True)
class DoctorCheck:
    name: str
    status: str
    detail: str


def run_doctor(
    root: str | Path = ".",
    *,
    claim_path: str | Path | None = None,
    require_docker: bool = False,
) -> dict[str, Any]:
    project_root = Path(root).resolve()
    checks: list[DoctorCheck] = []

    checks.append(
        DoctorCheck(
            "python",
            "PASS" if sys.version_info >= (3, 11) else "FAIL",
            f"{sys.version.split()[0]} (requires >=3.11)",
        )
    )
    checks.append(DoctorCheck("reprocert", "PASS", f"aetherx-reprocert {__version__}"))

    writable = project_root.is_dir() and os.access(project_root, os.W_OK)
    checks.append(
        DoctorCheck(
            "project_directory",
            "PASS" if writable else "FAIL",
            str(project_root),
        )
    )

    git = shutil.which("git")
    if git:
        inside = _git_inside(project_root)
        checks.append(
            DoctorCheck(
                "git",
                "PASS" if inside else "WARN",
                "repository detected" if inside else "git installed; target is not a git work tree",
            )
        )
    else:
        checks.append(
            DoctorCheck(
                "git",
                "WARN",
                "git executable not found; local ReproCert execution still works",
            )
        )

    resolved_claim = (
        Path(claim_path)
        if claim_path is not None
        else project_root / "reprocert.yml"
    )
    if not resolved_claim.is_absolute():
        resolved_claim = project_root / resolved_claim
    resolved_claim = resolved_claim.resolve()

    claim = None
    if resolved_claim.is_file():
        try:
            claim = load_claim(resolved_claim)
            checks.append(
                DoctorCheck(
                    "claim",
                    "PASS",
                    f"{claim.claim_id} ({resolved_claim})",
                )
            )
        except (ClaimError, OSError, ValueError) as exc:
            checks.append(DoctorCheck("claim", "FAIL", str(exc)))
    else:
        checks.append(
            DoctorCheck(
                "claim",
                "WARN",
                f"not found: {resolved_claim}; run 'reprocert init'",
            )
        )

    docker_required = require_docker or bool(claim is not None and "container" in claim.spec)
    docker = shutil.which("docker")
    if docker:
        available, detail = _docker_status(project_root)
        status = "PASS" if available else ("FAIL" if docker_required else "WARN")
        checks.append(DoctorCheck("docker", status, detail))
    elif docker_required:
        checks.append(
            DoctorCheck(
                "docker",
                "FAIL",
                "docker is required by the selected claim but was not found",
            )
        )
    else:
        checks.append(
            DoctorCheck(
                "docker",
                "INFO",
                "not installed; only required for container-profile claims",
            )
        )

    workflow = project_root / ".github" / "workflows" / "reprocert.yml"
    checks.append(
        DoctorCheck(
            "github_actions",
            "PASS" if workflow.is_file() else "INFO",
            str(workflow)
            if workflow.is_file()
            else "not configured; run 'reprocert init <profile> --github-actions'",
        )
    )

    status = "FAIL" if any(check.status == "FAIL" for check in checks) else "PASS"
    return {
        "status": status,
        "root": str(project_root),
        "checks": [
            {"name": check.name, "status": check.status, "detail": check.detail}
            for check in checks
        ],
    }


def _git_inside(root: Path) -> bool:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return completed.returncode == 0 and completed.stdout.strip() == "true"
    except (OSError, subprocess.SubprocessError):
        return False


def _docker_status(root: Path) -> tuple[bool, str]:
    try:
        completed = subprocess.run(
            ["docker", "version", "--format", "{{.Server.Version}}"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, f"docker check failed: {exc}"

    if completed.returncode == 0:
        return True, f"server {completed.stdout.strip() or 'available'}"
    detail = completed.stderr.strip() or completed.stdout.strip() or "docker daemon unavailable"
    return False, detail
