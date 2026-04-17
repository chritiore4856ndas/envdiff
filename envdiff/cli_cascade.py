"""CLI integration for cascade diff."""
from __future__ import annotations
import json
import click
from envdiff.differ_cascade import cascade_diff


def cascade_options(cmd):
    cmd = click.option(
        "--cascade",
        multiple=True,
        metavar="FILE",
        help="Chain of .env files to compare in order (repeat flag for each file).",
    )(cmd)
    cmd = click.option(
        "--cascade-json",
        is_flag=True,
        default=False,
        help="Output cascade report as JSON.",
    )(cmd)
    return cmd


def apply_cascade(cascade, cascade_json, **_kwargs) -> bool:
    """Run cascade diff if --cascade files were provided.

    Returns True if cascade mode was active (caller should exit after).
    """
    if not cascade:
        return False

    if len(cascade) < 2:
        raise click.UsageError("--cascade requires at least two files.")

    report = cascade_diff(list(cascade))

    if cascade_json:
        click.echo(json.dumps(report.as_dict(), indent=2))
    else:
        if report.is_clean():
            click.echo("cascade: all steps identical ✓")
        else:
            for step in report.steps:
                click.echo(f"\n{step.from_file} → {step.to_file}")
                if step.result.only_in_a:
                    for k in sorted(step.result.only_in_a):
                        click.echo(f"  - {k} (only in {step.from_file})")
                if step.result.only_in_b:
                    for k in sorted(step.result.only_in_b):
                        click.echo(f"  + {k} (only in {step.to_file})")
                if step.result.mismatched:
                    for k in sorted(step.result.mismatched):
                        click.echo(f"  ~ {k} (value differs)")
            drifting = report.all_drifting_keys()
            if drifting:
                click.echo("\nmost drifting keys:")
                for k, count in list(drifting.items())[:5]:
                    click.echo(f"  {k}: drifts in {count} step(s)")

    return True
