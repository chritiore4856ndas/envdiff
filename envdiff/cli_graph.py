"""CLI option to print a co-occurrence graph summary."""
from __future__ import annotations
import click
from typing import List
from envdiff.comparator import DiffResult
from envdiff.differ_graph import build_graph


def graph_options(f):
    f = click.option("--graph", is_flag=True, default=False, help="Print key co-occurrence graph.")(f)
    return f


def apply_graph(results: List[DiffResult], graph: bool) -> bool:
    """Print graph report if requested. Returns True if flag was active."""
    if not graph:
        return False

    report = build_graph(results)

    if not report.nodes:
        click.echo("Graph: no differing keys found.")
        return True

    click.echo("=== Key Co-occurrence Graph ===")
    click.echo(f"Nodes ({len(report.nodes)}):")
    for node in report.nodes:
        statuses = ", ".join(node.statuses)
        click.echo(f"  {node.key}  freq={node.frequency}  [{statuses}]")

    if report.edges:
        click.echo(f"Edges ({len(report.edges)}):")
        for edge in report.edges:
            click.echo(f"  {edge.key_a} -- {edge.key_b}  co={edge.co_occurrences}")
    else:
        click.echo("Edges: none")

    return True
