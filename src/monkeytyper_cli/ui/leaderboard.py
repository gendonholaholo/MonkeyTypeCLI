# ui/leaderboard.py

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing import Dict, Any, List
import datetime

from monkeytyper_cli.api.models import LeaderboardEntry

console = Console()

def display_leaderboard(leaderboard_data: List[LeaderboardEntry], mode: str, language: str):
    if not leaderboard_data:
        console.print(Panel(f"[yellow]No leaderboard data available for {mode} ({language}).[/]", title="Leaderboard"))
        return

    title = f"🏆 Leaderboard - {mode.capitalize()} ({language.upper()}) 🏆"
    table = Table(title=title, show_header=True, header_style="bold cyan")

    table.add_column("Rank", style="dim", width=5, justify="right")
    table.add_column("Name", width=25)
    table.add_column("WPM", justify="right", style="green")
    table.add_column("Acc %", justify="right", style="blue")
    table.add_column("Raw", justify="right")
    table.add_column("Date", justify="right")

    for entry in leaderboard_data:
        rank_str = str(entry.rank) if entry.rank is not None else "-"
        name_str = entry.name or "-"
        wpm_str = f"{entry.wpm:.2f}" if entry.wpm is not None else "-"
        acc_str = f"{entry.acc:.2f}" if entry.acc is not None else "-"
        raw_str = f"{entry.raw:.2f}" if entry.raw is not None else "-"
        date_str = "-"
        if entry.timestamp:
            try:
                 date_str = datetime.datetime.fromtimestamp(entry.timestamp).strftime("%Y-%m-%d")
            except ValueError:
                 pass
        
        table.add_row(
            rank_str,
            name_str,
            wpm_str,
            acc_str,
            raw_str,
            date_str
        )

    console.print(Panel(table, border_style="cyan")) 