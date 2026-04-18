"""CLI integration for key coupling analysis."""
from __future__ import annotations
import json
import click
from envdiff.differ_coupling import coupling_report, CouplingReport


def _format_coupling(report: CouplingReport, threshold: float, fmt: str) -> str:
    strong = report.strong(threshold)
    if fmt == "json":
        return json.dumps({"strong_pairs": [p.as_dict() for p in strong]}, indent=2)
    lines = []
    if not strong:
        lines.append("No strongly coupled key pairs found.")
    else:
        lines.append(f"Strongly coupled pairs (threshold={threshold}):")
        for p in strong:
            lines.append(
                f"  {p.key_a} <-> {p.key_b}  "
                f"co_changes={p.co_changes}/{p.total_snapshots}  "
                f"ratio={p.coupling_ratio():.2f}"
            )
    return "\n".join(lines)


def coupling_options(f):
    f = click.option(
        "--coupling",
        is_flag=True,
        default=False,
        help="Show keys that change together across results.",
    )(f)
    f = click.option(
        "--coupling-threshold",
        default=0.8,
        show_default=True,
        type=float,
        help="Minimum co-change ratio to report a pair.",
    )(f)
    f = click.option(
        "--coupling-format",
        default="text",
        type=click.Choice(["text", "json"]),
        show_default=True,
        help="Output format for coupling report.",
    )(f)
    return f


def apply_coupling(enabled: bool, results, threshold: float, fmt: str) -> bool:
    if not enabled:
        return False
    report = coupling_report(results)
    click.echo(_format_coupling(report, threshold, fmt))
    return True
