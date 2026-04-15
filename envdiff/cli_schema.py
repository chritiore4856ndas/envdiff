"""CLI integration for schema validation against a .env file."""
from __future__ import annotations

import sys
import click

from envdiff.parser import parse_env_file
from envdiff.schema import load_schema, validate


def schema_options(cmd: click.BaseCommand) -> click.BaseCommand:
    """Attach --schema option to a Click command."""
    cmd = click.option(
        "--schema",
        "schema_path",
        default=None,
        metavar="FILE",
        help="Path to a JSON schema file to validate keys against.",
    )(cmd)
    return cmd


def apply_schema(
    schema_path: str | None,
    env_file: str,
    *,
    exit_on_violation: bool = True,
) -> None:
    """Load *schema_path* and validate the parsed *env_file*.

    Prints violations to stdout.  If *exit_on_violation* is True and any
    violations are found, the process exits with code 2.
    """
    if schema_path is None:
        return

    rules = load_schema(schema_path)
    env = parse_env_file(env_file)
    result = validate(rules, env)

    if result.ok:
        click.echo("Schema validation passed.")
        return

    click.echo(f"Schema violations in {env_file}:")
    for v in result.violations:
        tag = "[missing]" if v.value is None else "[invalid]"
        click.echo(f"  {tag} {v.key}: {v.message}")

    if exit_on_violation:
        sys.exit(2)
