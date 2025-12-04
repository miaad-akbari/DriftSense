"""Command line interface for DriftSense."""

from __future__ import annotations

import argparse
import sys
from typing import List

from rich.console import Console

from . import diff_engine, manifest_loader, report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="driftsense",
        description="Detect configuration drift between desired and actual Kubernetes manifests.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Compare two manifest directories.")
    scan_parser.add_argument("desired_dir", help="Directory containing desired manifests.")
    scan_parser.add_argument("actual_dir", help="Directory containing actual manifests.")
    scan_parser.add_argument(
        "-f",
        "--format",
        choices=("text", "markdown", "json"),
        default="text",
        help="Output format (default: text).",
    )
    scan_parser.add_argument(
        "--ignore-kind",
        action="append",
        default=[],
        help="Kinds to ignore (repeatable).",
    )
    scan_parser.add_argument(
        "--fail-on-drift",
        action="store_true",
        help="Return exit code 1 if drift is detected.",
    )
    return parser


def handle_scan(args: argparse.Namespace, console: Console) -> int:
    desired_dir = manifest_loader.ensure_directory(args.desired_dir)
    actual_dir = manifest_loader.ensure_directory(args.actual_dir)

    desired_manifests = manifest_loader.load_manifests(desired_dir)
    actual_manifests = manifest_loader.load_manifests(actual_dir)
    ignore_kinds: List[str] = args.ignore_kind or []

    drift_report = diff_engine.compare(
        desired_manifests,
        actual_manifests,
        ignore_kinds=ignore_kinds,
    )

    if args.format == "text":
        report.print_text_report(drift_report, console)
    elif args.format == "markdown":
        console.print(report.render_markdown(drift_report))
    elif args.format == "json":
        console.print_json(data=drift_report.to_dict())

    if args.fail_on_drift and drift_report.has_drift():
        return 1
    return 0


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    console = Console()

    if args.command == "scan":
        return handle_scan(args, console)
    parser.print_help()
    return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
