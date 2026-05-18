"""Pipeline orchestrator — wires 4 agents together with structured data passing."""

import json
import time
import yaml
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.agents import lineage_scanner, dependency_mapper, impact_analyzer, compliance_checker

console = Console()


def load_schema(path: str) -> str:
    """Load a schema file (YAML/JSON) and return formatted text."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    with open(p, "r", encoding="utf-8") as f:
        content = f.read()
    if p.suffix in (".yaml", ".yml"):
        data = yaml.safe_load(content)
        return json.dumps(data, ensure_ascii=False, indent=2)
    return content


class DataLineagePipeline:
    """DataLineage pipeline: Lineage Scanner -> Dependency Mapper -> Impact Analyzer -> Compliance Checker."""

    def __init__(self):
        self.lineage = {}
        self.dependencies = {}
        self.impact = {}
        self.compliance = {}

    def run(self, input_path: str, target_table: str = "", skip_impact: bool = False, skip_compliance: bool = False) -> dict:
        """Execute the full 4-agent pipeline."""
        t0 = time.time()

        # Stage 1: Lineage Scanner
        console.print(Panel.fit(
            "[bold blue]STAGE 1/4: Lineage Scanner Agent[/] — scanning data sources",
            border_style="blue"
        ))
        schema_text = load_schema(input_path)
        self.lineage = lineage_scanner.run(schema_text)
        self._print_lineage_summary()

        # Stage 2: Dependency Mapper
        console.print(Panel.fit(
            "[bold yellow]STAGE 2/4: Dependency Mapper Agent[/] — mapping dependencies",
            border_style="yellow"
        ))
        self.dependencies = dependency_mapper.run(schema_text, self.lineage)
        self._print_dependency_summary()

        # Stage 3: Impact Analyzer
        if not skip_impact:
            console.print(Panel.fit(
                "[bold green]STAGE 3/4: Impact Analyzer Agent[/] — analyzing change impact",
                border_style="green"
            ))
            self.impact = impact_analyzer.run(schema_text, self.lineage, self.dependencies, target_table)
            self._print_impact_summary()
        else:
            console.print("[dim]Stage 3/4: Impact Analyzer — skipped[/]")

        # Stage 4: Compliance Checker
        if not skip_compliance:
            console.print(Panel.fit(
                "[bold red]STAGE 4/4: Compliance Checker Agent[/] — checking governance",
                border_style="red"
            ))
            self.compliance = compliance_checker.run(schema_text, self.lineage, self.dependencies)
            self._print_compliance_summary()
        else:
            console.print("[dim]Stage 4/4: Compliance Checker — skipped[/]")

        elapsed = time.time() - t0

        # Final summary
        console.print()
        console.print(Panel.fit(
            f"[bold]Pipeline Complete[/]\n"
            f"Time: {elapsed:.1f}s\n"
            f"Tables: {self.lineage.get('total_tables', '?')}\n"
            f"Lineage Edges: {self.lineage.get('lineage_edges', []) and len(self.lineage.get('lineage_edges', [])) or '?'}\n"
            f"Compliance Score: {self.compliance.get('overall_score', 'N/A')}",
            border_style="green"
        ))

        return {
            "pipeline": "DataLineage",
            "elapsed_seconds": round(elapsed, 2),
            "lineage": self.lineage,
            "dependencies": self.dependencies,
            "impact": self.impact,
            "compliance": self.compliance,
        }

    def _print_lineage_summary(self):
        table = Table(title="Lineage Scan Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_row("Total Tables", str(self.lineage.get("total_tables", "?")))
        table.add_row("Source Tables", str(self.lineage.get("source_tables", "?")))
        table.add_row("Derived Tables", str(self.lineage.get("derived_tables", "?")))
        edges = self.lineage.get("lineage_edges", [])
        table.add_row("Lineage Edges", str(len(edges)))
        metrics = self.lineage.get("metrics", {})
        table.add_row("Max Chain Depth", str(metrics.get("max_chain_depth", "?")))
        table.add_row("Orphan Columns", str(metrics.get("orphan_columns", "?")))
        console.print(table)

        # Print edge details
        for edge in edges[:5]:
            console.print(
                f"  [dim]{edge.get('source_table', '?')}[/] -> "
                f"[bold]{edge.get('target_table', '?')}[/] "
                f"({edge.get('transformation', '?')})"
            )
        if len(edges) > 5:
            console.print(f"  [dim]... and {len(edges) - 5} more edges[/]")

    def _print_dependency_summary(self):
        graph = self.dependencies.get("dependency_graph", {})
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        console.print(f"[yellow]Dependency Graph:[/] {len(nodes)} nodes, {len(edges)} edges")

        bottlenecks = self.dependencies.get("bottlenecks", [])
        console.print(f"[yellow]Bottlenecks:[/] {len(bottlenecks)}")
        for b in bottlenecks[:3]:
            console.print(f"  - [bold]{b.get('table', '?')}[/]: {b.get('reason', '')}")

        circular = self.dependencies.get("circular_dependencies", [])
        if circular:
            console.print(f"[red]Circular Dependencies:[/] {len(circular)}")
            for c in circular:
                console.print(f"  - {' -> '.join(c.get('tables', []))}")

    def _print_impact_summary(self):
        direct = self.impact.get("impact_analysis", {}).get("direct_impact", [])
        indirect = self.impact.get("impact_analysis", {}).get("indirect_impact", [])
        pipelines = self.impact.get("affected_pipelines", [])
        table = Table(title="Impact Analysis")
        table.add_column("Category", style="cyan")
        table.add_column("Count", style="magenta")
        table.add_column("Severity", style="red")
        table.add_row("Direct Impact", str(len(direct)), self.impact.get("overall_risk", "?"))
        table.add_row("Indirect Impact", str(len(indirect)), "")
        table.add_row("Affected Pipelines", str(len(pipelines)), "")
        console.print(table)

        for item in direct[:3]:
            console.print(
                f"  - [bold]{item.get('table', '?')}[/]: {item.get('severity', '?')} "
                f"— {item.get('description', '')[:80]}"
            )
        console.print(f"  [bold]Recommendation:[/] {self.impact.get('recommendation', '?')}")

    def _print_compliance_summary(self):
        checks = self.compliance.get("checks", [])
        passed = sum(1 for c in checks if c.get("status") == "pass")
        failed = sum(1 for c in checks if c.get("status") == "fail")
        warnings = sum(1 for c in checks if c.get("status") == "warning")
        table = Table(title="Compliance Check Results")
        table.add_column("Category", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Count", style="white")
        table.add_row("Passed", "[green]PASS[/]", str(passed))
        table.add_row("Failed", "[red]FAIL[/]", str(failed))
        table.add_row("Warnings", "[yellow]WARN[/]", str(warnings))
        table.add_row("Overall Score", "[bold]", str(self.compliance.get("overall_score", "?")))
        table.add_row("Status", "[bold]", str(self.compliance.get("compliance_status", "?")))
        console.print(table)

        pii = self.compliance.get("pii_inventory", [])
        if pii:
            console.print(f"[red]PII Columns Found:[/] {len(pii)}")
            for p in pii[:3]:
                console.print(f"  - {p.get('table', '?')}.{p.get('column', '?')} ({p.get('pii_type', '?')})")

        recs = self.compliance.get("recommendations", [])
        if recs:
            console.print(f"[yellow]Top Recommendations:[/]")
            for r in recs[:3]:
                console.print(f"  {r.get('priority', '?')}. [{r.get('category', '?')}] {r.get('action', '')}")
