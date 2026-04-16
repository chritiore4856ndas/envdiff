"""CLI integration for tag-based filtering and display."""

import click
from envdiff.tagger import tag_diff


def tag_options(func):
    """Decorator that adds --tag-rules and --filter-tag options to a command."""
    func = click.option(
        "--tag-rules",
        "tag_rules",
        multiple=True,
        metavar="PATTERN:TAG",
        help="Assign TAG to keys matching PATTERN glob (e.g. 'DB_*:database').",
    )(func)
    func = click.option(
        "--filter-tag",
        "filter_tag",
        default=None,
        metavar="TAG",
        help="Only show keys that have been assigned this tag.",
    )(func)
    return func


def apply_tags(diff_result, tag_rules, filter_tag):
    """Apply tag rules to a DiffResult and optionally filter by tag.

    Parameters
    ----------
    diff_result:
        A ``DiffResult`` instance from ``envdiff.comparator``.
    tag_rules:
        Iterable of strings in ``PATTERN:TAG`` format.
    filter_tag:
        If given, only keys carrying this tag are kept in the returned result.

    Returns
    -------
    DiffResult
        Possibly filtered diff result.
    """
    if not tag_rules and not filter_tag:
        return diff_result

    # Parse "PATTERN:TAG" strings into a dict mapping tag -> [patterns]
    rules: dict[str, list[str]] = {}
    for rule in tag_rules:
        if ":" not in rule:
            raise click.BadParameter(
                f"Tag rule {rule!r} must be in PATTERN:TAG format.",
                param_hint="--tag-rules",
            )
        pattern, tag = rule.split(":", 1)
        rules.setdefault(tag, []).append(pattern)

    tagged = tag_diff(diff_result, rules)

    if not filter_tag:
        return diff_result

    # Restrict diff_result to keys that carry filter_tag
    matching_keys = tagged.keys_for_tag(filter_tag)

    from envdiff.comparator import DiffResult

    return DiffResult(
        only_in_a={k: v for k, v in diff_result.only_in_a.items() if k in matching_keys},
        only_in_b={k: v for k, v in diff_result.only_in_b.items() if k in matching_keys},
        mismatched={
            k: v for k, v in diff_result.mismatched.items() if k in matching_keys
        },
        matching={k: v for k, v in diff_result.matching.items() if k in matching_keys},
    )
