"""Collect deterministic, machine-readable developer environment checks."""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import Any, Mapping


def check_python(minimum: tuple[int, int] = (3, 10)) -> dict[str, Any]:
    current = (sys.version_info.major, sys.version_info.minor)
    passed = current >= minimum
    return {
        "name": "python_version",
        "status": "pass" if passed else "fail",
        "message": f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "details": {"current": ".".join(map(str, current)), "minimum": ".".join(map(str, minimum))},
    }


def check_disk(path: str | Path = ".") -> dict[str, Any]:
    try:
        target = Path(path).expanduser().resolve(strict=True)
        usage = shutil.disk_usage(target)
        return {
            "name": "disk_space",
            "status": "pass" if usage.free > 0 else "fail",
            "message": f"{usage.free} bytes free on {target}",
            "details": {
                "path": str(target),
                "total_bytes": usage.total,
                "used_bytes": usage.used,
                "free_bytes": usage.free,
            },
        }
    except (OSError, RuntimeError) as exc:
        return {
            "name": "disk_space",
            "status": "fail",
            "message": f"Unable to inspect disk path: {exc}",
            "details": {"path": str(path), "error_type": type(exc).__name__},
        }


def check_environment(required: list[str] | None = None, environ: Mapping[str, str] | None = None) -> dict[str, Any]:
    """Check presence, not values, of selected environment variables."""
    required = required if required is not None else ["PATH"]
    env = os.environ if environ is None else environ
    missing = sorted(name for name in required if not env.get(name))
    return {
        "name": "environment_variables",
        "status": "pass" if not missing else "fail",
        "message": "All required variables are set" if not missing else f"Missing variables: {', '.join(missing)}",
        "details": {"required": sorted(required), "missing": missing},
    }


def check_tools(tools: list[str] | None = None) -> dict[str, Any]:
    tools = tools if tools is not None else ["git", "python"]
    found = {name: shutil.which(name) for name in sorted(set(tools))}
    missing = [name for name, location in found.items() if location is None]
    return {
        "name": "developer_tools",
        "status": "pass" if not missing else "fail",
        "message": "All configured tools are available" if not missing else f"Missing tools: {', '.join(missing)}",
        "details": {"found": found, "missing": missing},
    }


def load_config(path: str | Path) -> dict[str, Any]:
    """Load and validate JSON configuration; raise ValueError with useful details."""
    import json

    config_path = Path(path).expanduser()
    if not config_path.exists():
        raise ValueError(f"Configuration file does not exist: {config_path}")
    if not config_path.is_file():
        raise ValueError(f"Configuration path is not a file: {config_path}")
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid configuration file {config_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Configuration root must be a JSON object")
    required_env = data.get("required_env", ["PATH"])
    tools = data.get("tools", ["git", "python"])
    disk_path = data.get("disk_path", ".")
    if not isinstance(required_env, list) or not all(isinstance(x, str) and x for x in required_env):
        raise ValueError("'required_env' must be a list of non-empty strings")
    if not isinstance(tools, list) or not all(isinstance(x, str) and x for x in tools):
        raise ValueError("'tools' must be a list of non-empty strings")
    if not isinstance(disk_path, str) or not disk_path:
        raise ValueError("'disk_path' must be a non-empty string")
    return {"required_env": required_env, "tools": tools, "disk_path": disk_path}


def run_diagnostics(config: dict[str, Any] | None = None) -> dict[str, Any]:
    config = config or {"required_env": ["PATH"], "tools": ["git", "python"], "disk_path": "."}
    checks = [
        check_python(),
        check_disk(config["disk_path"]),
        check_environment(config["required_env"]),
        check_tools(config["tools"]),
    ]
    failed = sum(check["status"] == "fail" for check in checks)
    return {
        "tool": "devcheck",
        "version": "1.0.0",
        "overall_status": "pass" if failed == 0 else "fail",
        "summary": {"total": len(checks), "passed": len(checks) - failed, "failed": failed},
        "checks": checks,
    }
