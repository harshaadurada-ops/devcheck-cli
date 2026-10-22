"""Command-line interface for DevCheck."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .diagnostics import load_config, run_diagnostics
from .report import render_json, render_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="devcheck",
        description="Inspect a developer environment and produce a health report.",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text", help="report format (default: text)")
    parser.add_argument("--config", help="path to a JSON configuration file")
    parser.add_argument("--output", help="write report to this file instead of standard output")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        config = load_config(args.config) if args.config else None
    except ValueError as exc:
        print(f"devcheck: configuration error: {exc}", file=sys.stderr)
        return 2

    report = run_diagnostics(config)
    output = render_json(report) if args.format == "json" else render_text(report)
    if args.output:
        try:
            Path(args.output).expanduser().write_text(output, encoding="utf-8")
        except OSError as exc:
            print(f"devcheck: cannot write report: {exc}", file=sys.stderr)
            return 2
    else:
        sys.stdout.write(output)
    return 0 if report["overall_status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
