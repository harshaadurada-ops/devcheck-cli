"""Render diagnostic results as JSON or plain text."""
from __future__ import annotations

import json
from typing import Any


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def render_text(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "DevCheck Environment Health Report",
        "=" * 34,
        f"Overall status: {report['overall_status'].upper()}",
        f"Checks: {summary['passed']} passed, {summary['failed']} failed, {summary['total']} total",
        "",
    ]
    for check in report["checks"]:
        lines.append(f"[{check['status'].upper()}] {check['name']}: {check['message']}")
    return "\n".join(lines) + "\n"
