"""CLI commands for managing named environment profiles."""
from __future__ import annotations

import click

from envdiff.profiler import (
    save_profile,
    get_profile,
    delete_profile,
    list_profiles,
)


@click.group("profile")
def profile_group() -> None:
    """Manage named profiles (sets of .env files)."""


@profile_group.command("save")
@click.argument("name")
@click.argument("files", nargs=-1, required=True)
def save_cmd(name: str, files: tuple) -> None:
    """Save a named profile mapping to one or more .env file paths."""
    save_profile(name, list(files))
    click.echo(f"Profile '{name}' saved with {len(files)} file(s).")


@profile_group.command("show")
@click.argument("name")
def show_cmd(name: str) -> None:
    """Show file paths registered under a profile."""
    try:
        paths = get_profile(name)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Profile '{name}':")
    for p in paths:
        click.echo(f"  {p}")


@profile_group.command("delete")
@click.argument("name")
def delete_cmd(name: str) -> None:
    """Delete a saved profile."""
    removed = delete_profile(name)
    if removed:
        click.echo(f"Profile '{name}' deleted.")
    else:
        raise click.ClickException(f"Profile '{name}' not found.")


@profile_group.command("list")
def list_cmd() -> None:
    """List all saved profile names."""
    names = list_profiles()
    if not names:
        click.echo("No profiles saved.")
        return
    for name in names:
        click.echo(name)
