"""DataLineage CLI — multi-agent data lineage tracking and impact analysis pipeline."""

import sys
import os
import json
import click
from rich.console import Console
from rich.panel import Panel

from src.pipeline import DataLineagePipeline

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="datalineage")
def cli():
    """DataLineage — AI-powered multi-agent data lineage tracking & impact analysis pipeline.

    Four specialized agents collaborate in sequence:
    Lineage Scanner -> Dependency Mapper -> Impact Analyzer -> Compliance Checker
    """


@cli.command()
@click.option("--input", "-i", "input_path", required=True, help="Path to schema file (YAML/JSON)")
@click.option("--output", "-o", default="./output", help="Output directory")
@click.option("--target", "-t", default="", help="Target table for impact analysis (optional)")
def scan(input_path, output, target):
    """Run the full DataLineage pipeline."""
    console.print(Panel.fit(
        "[bold]DataLineage Pipeline[/]\n"
        f"Input: {input_path}\n"
        f"Target: {target or 'full scan'}",
        border_style="blue"
    ))

    try:
        pipeline = DataLineagePipeline()
        result = pipeline.run(input_path, target_table=target)

        os.makedirs(output, exist_ok=True)
        out_path = os.path.join(output, "datalineage_report.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        console.print(f"\n[green]Report saved to {out_path}[/green]")

    except ValueError as e:
        console.print(f"[red]Configuration Error:[/] {e}")
        console.print("[dim]Make sure DEEPSEEK_API_KEY is set in your .env file[/]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected Error:[/] {e}")
        sys.exit(1)


@cli.command()
@click.option("--input", "-i", "input_path", required=True, help="Path to schema file (YAML/JSON)")
@click.option("--output", "-o", default="./output", help="Output directory")
def map(input_path, output):
    """Run Lineage Scanner + Dependency Mapper only (first 2 stages)."""
    console.print(Panel.fit(
        "[bold]DataLineage — Dependency Mapping[/]\n"
        f"Input: {input_path}",
        border_style="yellow"
    ))

    try:
        pipeline = DataLineagePipeline()
        result = pipeline.run(input_path, skip_impact=True, skip_compliance=True)

        os.makedirs(output, exist_ok=True)
        out_path = os.path.join(output, "datalineage_map.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        console.print(f"\n[green]Map saved to {out_path}[/green]")

    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        sys.exit(1)


@cli.command()
@click.option("--input", "-i", "input_path", required=True, help="Path to schema file (YAML/JSON)")
@click.option("--target", "-t", required=True, help="Target table to analyze impact for")
@click.option("--output", "-o", default="./output", help="Output directory")
def impact(input_path, target, output):
    """Analyze impact of schema changes on target table."""
    console.print(Panel.fit(
        "[bold]DataLineage — Impact Analysis[/]\n"
        f"Input: {input_path}\n"
        f"Target: {target}",
        border_style="green"
    ))

    try:
        pipeline = DataLineagePipeline()
        result = pipeline.run(input_path, target_table=target, skip_compliance=True)

        os.makedirs(output, exist_ok=True)
        out_path = os.path.join(output, "datalineage_impact.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        console.print(f"\n[green]Impact report saved to {out_path}[/green]")

    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        sys.exit(1)


@cli.command()
@click.option("--input", "-i", "input_path", required=True, help="Path to schema file (YAML/JSON)")
@click.option("--output", "-o", default="./output", help="Output directory")
def compliance(input_path, output):
    """Check data governance compliance."""
    console.print(Panel.fit(
        "[bold]DataLineage — Compliance Check[/]\n"
        f"Input: {input_path}",
        border_style="red"
    ))

    try:
        pipeline = DataLineagePipeline()
        result = pipeline.run(input_path, skip_impact=True)

        os.makedirs(output, exist_ok=True)
        out_path = os.path.join(output, "datalineage_compliance.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        console.print(f"\n[green]Compliance report saved to {out_path}[/green]")

    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        sys.exit(1)


@cli.command()
@click.option("--input", "-i", "input_path", required=True, help="Path to pipeline JSON report")
def report(input_path):
    """Display a saved pipeline report."""
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        console.print(Panel("[bold]DataLineage Report[/bold]"))
        for key in ("lineage", "dependencies", "impact", "compliance"):
            section = data.get(key, {})
            if section:
                console.print(f"\n[bold cyan]{key.upper()}[/bold cyan]")
                console.print(json.dumps(section, ensure_ascii=False, indent=2)[:2000])

    except FileNotFoundError:
        console.print(f"[red]File not found:[/] {input_path}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
