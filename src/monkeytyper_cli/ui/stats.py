# ui/stats.py

from rich.console import Console
from rich.panel import Panel
from typing import Dict, Any
from rich.table import Table
import datetime

# Import the Pydantic models
from monkeytyper_cli.api.models import UserStatsData, PersonalBestsData, PersonalBestEntry

console = Console()

def display_stats(stats_data: UserStatsData):
    """Displays user statistics in a table."""
    table = Table(title="📊 User Stats", show_header=False, border_style="blue")
    table.add_column("Metric", style="dim")
    table.add_column("Value")

    if stats_data.testsStarted is not None:
        table.add_row("Tests Started", str(stats_data.testsStarted))
    if stats_data.testsCompleted is not None:
        table.add_row("Tests Completed", str(stats_data.testsCompleted))
    if stats_data.timeTyping is not None:
        # Format time typing (assuming seconds)
        duration = datetime.timedelta(seconds=stats_data.timeTyping)
        table.add_row("Time Typing", str(duration))
    # Add more rows as fields are confirmed in UserStatsData
    
    if table.row_count > 0:
        console.print(Panel(table, border_style="blue"))
    else:
         console.print(Panel("[yellow]No user stats data available to display.[/]", title="User Stats"))

def display_personal_bests(bests_data: PersonalBestsData):
    """Displays personal bests in a table."""
    if not bests_data or not bests_data.bests:
        console.print(Panel("[yellow]No personal bests data available.[/]", title="Personal Bests"))
        return

    table = Table(title="🏆 Personal Bests", show_header=True, header_style="bold magenta")
    table.add_column("Mode", style="dim", width=20)
    table.add_column("WPM", justify="right", style="green")
    table.add_column("Accuracy %", justify="right", style="blue")
    table.add_column("Raw WPM", justify="right")
    table.add_column("Consistency %", justify="right")
    table.add_column("Date", justify="right")

    # Sort bests by key (mode name) for consistent order
    sorted_modes = sorted(bests_data.bests.keys())

    for mode_key in sorted_modes:
        best = bests_data.bests[mode_key]
        if best: # Check if the entry exists
            wpm_str = f"{best.wpm:.2f}" if best.wpm is not None else "-"
            acc_str = f"{best.acc:.2f}" if best.acc is not None else "-"
            raw_str = f"{best.raw:.2f}" if best.raw is not None else "-"
            cons_str = f"{best.consistency:.2f}" if best.consistency is not None else "-"
            date_str = "-"
            if best.timestamp:
                try:
                     date_str = datetime.datetime.fromtimestamp(best.timestamp).strftime("%Y-%m-%d")
                except ValueError:
                     pass # Ignore invalid timestamp
            
            table.add_row(
                mode_key, # Display the mode identifier (e.g., "time_60")
                wpm_str,
                acc_str,
                raw_str,
                cons_str,
                date_str
            )

    if table.row_count > 0:
        console.print(Panel(table, border_style="magenta"))
    else:
        console.print(Panel("[yellow]No personal best entries found in data.[/]", title="Personal Bests")) 