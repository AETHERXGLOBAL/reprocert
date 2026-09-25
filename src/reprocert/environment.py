from __future__ import annotations

import os
import platform
import subprocess
import sys
from importlib import metadata
from pathlib import Path
from typing import Any


def capture_environment(working_dir: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "executable": Path(sys.executable).name,
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "ci": {
            "github_actions": os.getenv("GITHUB_ACTIONS") == "true",
            "repository": os.getenv("GITHUB_REPOSITORY"),
            "ref": os.getenv("GITHUB_REF"),
            "sha": os.getenv("GITHUB_SHA"),
            "run_id": os.getenv("GITHUB_RUN_ID"),
            "run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
            "workflow": os.getenv("GITHUB_WORKFLOW"),
        },
        "git": _capture_git(working_dir),
        "dependencies": _dependencies(),
    }
    return result


def _capture_git(working_dir: Path) -> dict[str, Any]:
    def run(*args: str) -> str | None:
        try:
            cp = subprocess.run(
                ["git", *args], cwd=working_dir, check=True, capture_output=True, text=True, timeout=5
            )
            return cp.stdout.strip()
        except (OSError, subprocess.SubprocessError):
            return None

    commit = run("rev-parse", "HEAD")
    top_level = run("rev-parse", "--show-toplevel")
    dirty_text = run("status", "--porcelain=v1")
    return {
        "commit": commit,
        "repository_root_detected": bool(top_level),
        "dirty": None if dirty_text is None else bool(dirty_text),
    }


def _dependencies() -> list[dict[str, str]]:
    pairs: list[dict[str, str]] = []
    for dist in metadata.distributions():
        name = dist.metadata.get("Name")
        version = dist.version
        if name:
            pairs.append({"name": str(name), "version": str(version)})
    pairs.sort(key=lambda x: x["name"].lower())
    return pairs
