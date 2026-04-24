"""CLI integration for the balance report feature."""
from __future__ import annotations

import json
from typing import List, Tuple

import click

from envdiff.comparator import DiffResult
from envdiff.differ_balance import BalanceReport, balance_results


def _format_report(report: BalanceReport, *, json_out: bool = False) -> str:
    if json_out:
        return json.dumps(report.as_dict(), indent=2)

    if not report.entries:
        return "(no environments to balance)"

    lines = ["Balance Report", "=" * 40]
    for entry in report.entries:
        status = "OK" if entry.is_balanced else "UNBALANCED"
        lines.append(
            f"  {entry.env_name:<20} score={entry.balance_score:.2f}  [{status}]"
        )
        if not entry.is_balanced:
            if entry.missing_keys:
                lines.append(f"    missing : {entry.missing_keys}")
            if entry.extra_keys:
                lines.append(f"    extra   : {entry.extra_keys}")
            if entry.mismatch_keys:
                lines.append(f"    mismatch: {entry.mismatch_keys}")
    return "\n".join(lines)


def balance_options(f):
    f = click.option(
        "--balance",
        is_flag=True,
        default=False,
        help="Show per-environment balance report.",
    )(f)
    f = click.option(
        "--balance-json",
        is_flag=True,
        default=False,
        help="Output balance report as JSON.",
    )(f)
    return f


def apply_balance(
    ctx_pairs: List[Tuple[str, DiffResult]],
    *,
    balance: bool,
    balance_json: bool,
) -> bool:
    """Print balance report if requested. Returns True if flag was active."""
    if not balance and not balance_json:
        return False

    report = balance_results(ctx_pairs)
    click.echo(_format_report(report, json_out=balance_json))
    return True
