"""CLI decorator that adds --tag options and prints tagged key groups."""

from __future__ import annotations

import functools
from typing import Callable

import click

from envdiff.tagger import tag_diff


def tag_options(cmd: Callable) -> Callable:
    """Decorator that adds ``--tag`` option to a Click command."""

    @click.option(
        "--tag",
        "tag_rules",
        multiple=True,
        metavar="LABEL:GLOB",
        help=(
            "Tag keys matching GLOB with LABEL.  "
            "May be repeated, e.g. --tag db:DB_* --tag secret:*SECRET*"
        ),
    )
    @functools.wraps(cmd)
    def wrapper(*args, **kwargs):
        return cmd(*args, **kwargs)

    return wrapper


def apply_tags(result, tag_rules: tuple[str, ...]) -> None:
    """Parse *tag_rules*, build a TaggedDiff, and print a tag summary.

    Silently does nothing when no rules are provided.
    """
    if not tag_rules:
        return

    rules: dict[str, list[str]] = {}
    for raw in tag_rules:
        if ":" not in raw:
            raise click.BadParameter(
                f"Expected LABEL:GLOB format, got {raw!r}",
                param_hint="--tag",
            )
        label, glob = raw.split(":", 1)
        rules.setdefault(label.strip(), []).append(glob.strip())

    tagged = tag_diff(result, rules)

    if not any(tagged.tags.values()):
        click.echo("[tags] no keys matched any tag rule")
        return

    click.echo("[tags]")
    for label in sorted(rules):
        keys = tagged.keys_for_tag(label)
        if keys:
            click.echo(f"  {label}: {', '.join(sorted(keys))}")
        else:
            click.echo(f"  {label}: (no matches)")
