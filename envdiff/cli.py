"""Command-line interface entry point for envdiff."""

import sys
from pathlib import Path

import click

from envdiff.comparator import compare, has_diff
from envdiff.formatter import Format, format_json, format_table, format_text
from envdiff.parser import parse_env_file


@click.command()
@click.argument("file_a", type=click.Path(exists=True, path_type=Path))
@click.argument("file_b", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json", "table"]),
    default="text",
    show_default=True,
    help="Output format.",
)
@click.option(
    "--no-color",
    is_flag=True,
    default=False,
    help="Disable ANSI color output.",
)
@click.option(
    "--exit-code",
    is_flag=True,
    default=False,
    help="Exit with code 1 if differences are found.",
)
def main(
    file_a: Path,
    file_b: Path,
    output_format: Format,
    no_color: bool,
    exit_code: bool,
) -> None:
    """Compare two .env files and report differences.

    FILE_A is treated as the reference (e.g. .env.example).
    FILE_B is the environment being checked (e.g. .env).
    """
    env_a = parse_env_file(file_a)
    env_b = parse_env_file(file_b)
    result = compare(env_a, env_b)

    use_color = not no_color

    if output_format == "json":
        click.echo(format_json(result))
    elif output_format == "table":
        click.echo(format_table(result, color=use_color))
    else:
        click.echo(format_text(result, color=use_color))

    if exit_code and has_diff(result):
        sys.exit(1)


if __name__ == "__main__":
    main()
