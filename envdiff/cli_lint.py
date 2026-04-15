"""CLI integration for the .env linter."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from envdiff.linter import LintIssue, LintResult, lint_env_file


def _fmt_issue(issue: LintIssue) -> str:
    tag = "[ERROR]" if issue.severity == "error" else "[WARN] "
    loc = f"line {issue.line_number}"
    key_part = f" ({issue.key})" if issue.key else ""
    return f"  {tag} {loc}{key_part}: {issue.message}"


def _print_result(result: LintResult) -> None:
    click.echo(f"\nLinting: {result.path}")
    if result.ok:
        click.echo("  OK — no issues found.")
        return
    for issue in result.issues:
        click.echo(_fmt_issue(issue))
    click.echo(
        f"  {len(result.errors)} error(s), {len(result.warnings)} warning(s)"
    )


def lint_options(cmd: click.BaseCommand) -> click.BaseCommand:
    """Decorator that adds --lint flags to an existing command."""
    cmd = click.option(
        "--lint",
        "lint_paths",
        multiple=True,
        metavar="FILE",
        help="Lint one or more .env files for style issues.",
    )(cmd)
    cmd = click.option(
        "--lint-strict",
        is_flag=True,
        default=False,
        help="Exit non-zero if any warnings are found (not just errors).",
    )(cmd)
    return cmd


def apply_lint(lint_paths: tuple[str, ...], lint_strict: bool) -> None:
    """Run linter over provided paths and exit if issues are found."""
    if not lint_paths:
        return

    any_error = False
    any_warning = False

    for p in lint_paths:
        result = lint_env_file(p)
        _print_result(result)
        if result.errors:
            any_error = True
        if result.warnings:
            any_warning = True

    if any_error or (lint_strict and any_warning):
        sys.exit(1)
