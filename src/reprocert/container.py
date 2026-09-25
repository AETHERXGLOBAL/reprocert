from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Any

IMAGE_DIGEST_RE = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._/:-]*@sha256:[a-f0-9]{64}$"
)


class ContainerProfileError(ValueError):
    pass


def validate_container_profile(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ContainerProfileError("spec.container must be an object")

    engine = raw.get("engine", "docker")
    if engine != "docker":
        raise ContainerProfileError(
            "Only the docker container engine is supported"
        )

    image = raw.get("image")
    if not isinstance(image, str) or not IMAGE_DIGEST_RE.fullmatch(image):
        raise ContainerProfileError(
            "spec.container.image must be pinned as "
            "name@sha256:<64 lowercase hex>"
        )

    if raw.get("network", "none") != "none":
        raise ContainerProfileError("Container network must be 'none'")

    for key in (
        "read_only_root",
        "drop_capabilities",
        "no_new_privileges",
        "run_as_host_user",
    ):
        if raw.get(key, True) is not True:
            raise ContainerProfileError(
                f"spec.container.{key} must remain true"
            )

    pids_limit = raw.get("pids_limit", 256)
    if (
        not isinstance(pids_limit, int)
        or isinstance(pids_limit, bool)
        or pids_limit < 16
        or pids_limit > 4096
    ):
        raise ContainerProfileError(
            "spec.container.pids_limit must be an integer "
            "between 16 and 4096"
        )

    return {
        "engine": "docker",
        "image": image,
        "network": "none",
        "read_only_root": True,
        "drop_capabilities": True,
        "no_new_privileges": True,
        "run_as_host_user": True,
        "pids_limit": pids_limit,
    }


def build_docker_command(
    profile: dict[str, Any],
    working_dir: Path,
    command: list[str],
) -> list[str]:
    validated = validate_container_profile(profile)

    if not hasattr(os, "getuid") or not hasattr(os, "getgid"):
        raise ContainerProfileError(
            "The hardened Docker profile currently requires a POSIX host "
            "with numeric UID/GID support"
        )

    uid = os.getuid()
    gid = os.getgid()
    mount = f"{working_dir.resolve()}:/workspace:rw"

    return [
        "docker",
        "run",
        "--rm",
        "--network",
        "none",
        "--read-only",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges:true",
        "--user",
        f"{uid}:{gid}",
        "--pids-limit",
        str(validated["pids_limit"]),
        "--tmpfs",
        "/tmp:rw,noexec,nosuid,size=64m",
        "--volume",
        mount,
        "--workdir",
        "/workspace",
        validated["image"],
        *command,
    ]


def docker_engine_metadata() -> dict[str, Any]:
    try:
        completed = subprocess.run(
            ["docker", "version", "--format", "{{.Server.Version}}"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        version = completed.stdout.strip() or None
        return {
            "engine": "docker",
            "server_version": version,
            "host_uid": os.getuid() if hasattr(os, "getuid") else None,
            "host_gid": os.getgid() if hasattr(os, "getgid") else None,
        }
    except (OSError, subprocess.SubprocessError):
        return {
            "engine": "docker",
            "server_version": None,
            "host_uid": os.getuid() if hasattr(os, "getuid") else None,
            "host_gid": os.getgid() if hasattr(os, "getgid") else None,
        }
