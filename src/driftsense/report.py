"""Reporting helpers for DriftSense."""

from __future__ import annotations

from typing import Iterable, List

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from .diff_engine import DriftReport, ManifestRecord


def _format_records(records: Iterable[ManifestRecord]) -> Table:
    table = Table(box=None)
    table.add_column("Resource")
    table.add_column("Source", style="dim")
    for record in records:
        table.add_row(record.key.human(), record.source)
    return table


def print_text_report(report: DriftReport, console: Console) -> None:
    if not report.has_drift():
        console.print("[bold green]No drift detected.[/bold green]")
        return

    console.print("[bold yellow]Drift detected![/bold yellow]")
    if report.missing:
        console.print(Panel(_format_records(report.missing), title="Missing in cluster"))
    if report.extra:
        console.print(Panel(_format_records(report.extra), title="Unexpected in cluster"))
    if report.changed:
        for changed in report.changed:
            console.rule(f"Changed: {changed.key.human()}")
            console.print(f"Desired: {changed.desired_source}")
            console.print(f"Actual : {changed.actual_source}")
            console.print(
                Syntax(changed.diff or "No diff available", "diff", theme="monokai", background_color="default")
            )


def render_markdown(report: DriftReport) -> str:
    if not report.has_drift():
        return ":white_check_mark: **No drift detected**"

    lines: List[str] = ["## Drift detected"]
    if report.missing:
        lines.append("\n### Missing in cluster")
        lines.append("| Resource | Source |")
        lines.append("| --- | --- |")
        for record in report.missing:
            lines.append(f"| `{record.key.human()}` | `{record.source}` |")
    if report.extra:
        lines.append("\n### Unexpected in cluster")
        lines.append("| Resource | Source |")
        lines.append("| --- | --- |")
        for record in report.extra:
            lines.append(f"| `{record.key.human()}` | `{record.source}` |")
    if report.changed:
        lines.append("\n### Changed resources")
        for changed in report.changed:
            lines.append(f"#### `{changed.key.human()}`")
            lines.append(
                f"* desired: `{changed.desired_source}` · actual: `{changed.actual_source}`\n"
                f"\n```diff\n{changed.diff}\n```"
            )
    return "\n".join(lines)
