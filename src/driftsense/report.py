"""Reporting helpers for DriftSense."""

from __future__ import annotations

from typing import Iterable, List

from .diff_engine import DriftReport, ManifestRecord


def _format_records_list(records: Iterable[ManifestRecord]) -> List[str]:
    return [f"- {record.key.human()} ({record.source})" for record in records]


def render_text(report: DriftReport) -> str:
    if not report.has_drift():
        return "No drift detected."

    lines: List[str] = ["Drift detected!"]
    if report.missing:
        lines.append("\nMissing in cluster:")
        lines.extend(_format_records_list(report.missing))
    if report.extra:
        lines.append("\nUnexpected in cluster:")
        lines.extend(_format_records_list(report.extra))
    if report.changed:
        lines.append("\nChanged resources:")
        for changed in report.changed:
            lines.append(
                f"- {changed.key.human()} :: desired {changed.desired_source} vs actual {changed.actual_source}"
            )
            if changed.diff:
                lines.append(changed.diff)
    return "\n".join(lines)


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
