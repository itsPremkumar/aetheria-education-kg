"""CLI interface for Education Knowledge Graph."""

from __future__ import annotations

import sys
from typing import Any

import click
from rich.console import Console
from rich.table import Table

from education_kg.models import ConceptDifficulty
from education_kg.pipeline import Pipeline

console = Console()
pipeline = Pipeline()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Education Knowledge Graph CLI."""
    pass


@cli.command()
@click.argument("text")
@click.option("--subject", "-s", default="", help="Subject area")
def extract(text: str, subject: str):
    """Extract concepts from text."""
    result = pipeline.process_text(text, subject)
    console.print(f"[green]Extracted {result.concepts_extracted} concepts[/green]")
    console.print(f"[blue]Found {result.relations_found} relations[/blue]")


@cli.command()
@click.argument("start")
@click.option("--goal", "-g", required=True, help="Goal concept")
def path(start: str, goal: str):
    """Generate learning path."""
    result = pipeline.generate_learning_path(start, goal)
    if result:
        console.print(f"[green]Learning Path: {result.title}[/green]")
        console.print(f"Concepts: {', '.join(result.concepts)}")
        console.print(f"Estimated: {result.estimated_hours} hours")
    else:
        console.print("[red]No path found[/red]")


@cli.command()
@click.argument("concept_ids", nargs=-1)
@click.option("--questions", "-q", default=5, help="Number of questions")
def quiz(concept_ids: tuple[str, ...], questions: int):
    """Generate quiz."""
    result = pipeline.generate_quiz(list(concept_ids), questions)
    console.print(f"[green]Quiz: {result.title}[/green]")
    for i, q in enumerate(result.questions, 1):
        console.print(f"\n[bold]Question {i}:[/bold] {q.question}")
        for j, option in enumerate(q.options):
            console.print(f"  {j + 1}. {option}")


@cli.command()
@click.argument("query")
def ask(query: str):
    """Ask a question."""
    result = pipeline.answer_question(query)
    console.print(f"[green]Answer:[/green] {result.answer}")
    console.print(f"Confidence: {result.confidence:.0%}")
    if result.reasoning_path:
        console.print(f"Path: {' → '.join(result.reasoning_path)}")


@cli.command()
def stats():
    """Show graph statistics."""
    graph = pipeline.get_graph()
    stats = graph.get_statistics()

    table = Table(title="Knowledge Graph Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Concepts", str(stats["total_concepts"]))
    table.add_row("Total Relations", str(stats["total_relations"]))
    table.add_row("Subjects", ", ".join(stats["subjects"]))

    for level, count in stats["difficulty_counts"].items():
        table.add_row(f"  {level.capitalize()}", str(count))

    console.print(table)


@cli.command()
def languages():
    """Show supported languages."""
    ml = pipeline.get_multilang()
    langs = ml.get_supported_languages()
    console.print("[green]Supported Languages:[/green]")
    for lang in langs:
        console.print(f"  {lang}: {ml.translate('welcome', lang)[:50]}...")


if __name__ == "__main__":
    cli()
