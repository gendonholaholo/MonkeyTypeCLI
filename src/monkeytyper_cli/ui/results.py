# Placeholder for displaying results (rich) 

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from monkeytyper_cli.core.models import TestResult

console = Console()

def display_results(result: TestResult):
    """Displays the final test results in a formatted table."""

    table = Table(title="🏁 Test Results 🏁", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="dim", width=20)
    table.add_column("Value", justify="right")

    table.add_row("WPM (Correct)", f"[bold green]{result.wpm:.2f}[/]")
    table.add_row("Accuracy", f"[bold blue]{result.accuracy:.2f}%[/]")
    table.add_row("Raw WPM", f"{result.raw_wpm:.2f}")
    table.add_row("Correct Characters", f"[green]{result.correct_chars}[/]")
    table.add_row("Incorrect Characters", f"[red]{result.incorrect_chars}[/]")
    table.add_row("Time Elapsed", f"{result.time_elapsed_seconds:.2f}s")
    table.add_row("Mode", f"{result.mode.value} ({result.config_value})")

    console.print(Panel(table, border_style="blue")) 