import typer
from typing_extensions import Annotated
import sys
import platform
import subprocess
import asyncio
from typing import List, Optional

if platform.system() == "Windows":
    import msvcrt
else:
    import tty
    import termios

from monkeytyper_cli import __version__
from monkeytyper_cli.config.settings import settings
from monkeytyper_cli.core.models import GameMode, TestState, Language, TestResult
from monkeytyper_cli.core import engine
from monkeytyper_cli.ui import prompts, results
from monkeytyper_cli.ui.prompts import console, create_prompt_display
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

from monkeytyper_cli.config.user_config import UserSettings

from monkeytyper_cli.api.client import APIClient, ApiClientError

from monkeytyper_cli.ui import stats as ui_stats
from monkeytyper_cli.ui import leaderboard as ui_leaderboard

# ANSI escape codes
CLEAR_SCREEN = "\033[2J\033[H"

def clear_terminal():
    """Clear the terminal screen."""
    if platform.system() == "Windows":
        subprocess.run("cls", shell=True)
    else:
        sys.stdout.write(CLEAR_SCREEN)
        sys.stdout.flush()

user_settings = UserSettings.load()

session_history: List[TestResult] = []

app = typer.Typer(
    name="monkeytyper-cli",
    help="🐒⌨️ A CLI for Monkeytype.",
    add_completion=False,
    no_args_is_help=False,
    invoke_without_command=True,
)

def version_callback(value: bool):
    if value:
        console.print(f"MonkeyTyper CLI Version: {__version__}")
        raise typer.Exit()

@app.callback()
def main_callback(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-V",
            help="Show application version and exit.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = False,
):
    global user_settings

    if ctx.invoked_subcommand is None:
        console.print(Panel("[bold cyan]Welcome to MonkeyTyper CLI![/]"), justify="center")
        show_main_menu()
        raise typer.Exit()

def _get_char() -> str:
    if platform.system() == "Windows":
        return msvcrt.getwch()
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            char = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return char

@app.command()
def start(
    mode: Annotated[
        GameMode,
        typer.Option(help="Typing test mode ('time' or 'words')."),
    ] = user_settings.default_mode,
    duration: Annotated[
        int,
        typer.Option("--duration", "-d", help="Duration in seconds (only for 'time' mode)."),
    ] = user_settings.default_duration,
    length: Annotated[
        int,
        typer.Option("--length", "-n", help="Number of words (only for 'words' mode)."),
    ] = user_settings.default_length,
    language: Annotated[
        Language,
        typer.Option("--language", "-l", help="Language for the typing test ('en' or 'id')."),
    ] = user_settings.default_language,
):
    if mode == GameMode.TIME:
        config_value = duration
        config_unit = "seconds"
    elif mode == GameMode.WORDS:
        config_value = length
        config_unit = "words"
    else:
        console.print(f"Error: Invalid mode '{mode.value}'.", style="bold red")
        raise typer.Exit(1)

    console.print(
        f"Starting test: Mode=[cyan]{mode.value}[/], "
        f"Config=[cyan]{config_value} {config_unit}[/], "
        f"Language=[cyan]{language.value}[/]"
    )
    console.print("Press any key to begin...")
    _get_char()

    try:
        game_state = engine.start_game(
            mode=mode, config_value=config_value, language=language.value
        )
    except (FileNotFoundError, IOError, ValueError) as e:
         console.print(f"[bold red]Error initializing game:[/bold red] {e}")
         raise typer.Exit(1)

    try:
        while not game_state.is_finished():
            clear_terminal()
            console.print(create_prompt_display(game_state))
            
            char = _get_char()
            if ord(char) == 3:
                raise typer.Exit()

            engine.process_input(game_state, char)

        if game_state.state != TestState.FINISHED:
            engine.finish_game(game_state)

        final_result = engine.calculate_results(game_state)

        console.print("\n" * 1)
        results.display_results(final_result)

        session_history.append(final_result)

    except typer.Exit:
        pass
    except Exception as e:
        console.print(f"\nAn unexpected error occurred: {e}", style="bold red")
        raise typer.Exit(1)
    finally:
        if platform.system() != "Windows":
            fd = sys.stdin.fileno()
            pass

def show_main_menu():
    while True:
        console.print("\n[bold]Main Menu:[/]")
        console.print("1. Start Typing Test")
        console.print("2. View Stats (Requires ApeKey)")
        console.print("3. View Leaderboard")
        console.print("4. Settings")
        console.print("5. Help")
        console.print("6. View Session History")
        console.print("7. Exit")

        choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4", "5", "6", "7"], default="1")

        if choice == '1':
            start_test_from_menu()
        elif choice == '2':
            _call_api_from_menu(view_stats)
        elif choice == '3':
            _call_api_from_menu(view_leaderboard)
        elif choice == '4':
            show_settings_menu()
        elif choice == '5':
            show_help()
        elif choice == '6':
            view_session_history()
        elif choice == '7':
             console.print("Goodbye!")
             break
        else:
            console.print("[red]Invalid choice.[/]")

def start_test_from_menu():
    console.print("\n[bold]Configure Typing Test:[/]")

    # Choose Language
    # lang_choices = {str(i+1): lang.value for i, lang in enumerate(Language)}
    lang_choices = {str(i+1): lang for i, lang in enumerate(Language)}
    console.print("Select Language:")
    for i, lang in lang_choices.items():
        console.print(f" {i}. {lang}")
    # Find the default language's number choice
    default_lang_num = "1"
    for num, val in lang_choices.items():
        if val == user_settings.default_language.value:
            default_lang_num = num
            break
    lang_choice_num = Prompt.ask(
        "Choose language",
        choices=list(lang_choices.keys()),
        default=default_lang_num # Use loaded setting dynamically
    )
    language = lang_choices[lang_choice_num]

    # Choose Mode
    mode_choices = {str(i+1): mode.value for i, mode in enumerate(GameMode)}
    console.print("Select Mode:")
    for i, mode_val in mode_choices.items():
        console.print(f" {i}. {mode_val}")
    default_mode_num = "1"
    for num, val in mode_choices.items():
         if val == user_settings.default_mode.value:
              default_mode_num = num
              break
    mode_choice_num = Prompt.ask(
        "Choose mode",
        choices=list(mode_choices.keys()),
        default=default_mode_num
    )
    mode_str = mode_choices[mode_choice_num]
    mode = GameMode(mode_str)

    if mode == GameMode.TIME:
        config_value = IntPrompt.ask("Enter duration (seconds)", default=user_settings.default_duration)
    elif mode == GameMode.WORDS:
        config_value = IntPrompt.ask("Enter number of words", default=user_settings.default_length)
    else:
        console.print(f"[red]Invalid mode selected: {mode}[/]")
        return

    console.print(f"\nStarting test: Language={language}, Mode={mode.value}, Value={config_value}")
    if Confirm.ask("Start now?", default=True):
        start(mode=mode, duration=config_value if mode == GameMode.TIME else 30, length=config_value if mode == GameMode.WORDS else 25, language=Language(language))
    else:
        console.print("Test cancelled.")

def show_settings_menu():
    global user_settings
    while True:
        console.print("\n[bold]User Settings:[/]")
        console.print(f"1. Default Language: [cyan]{user_settings.default_language.value}[/]")
        console.print(f"2. Default Mode: [cyan]{user_settings.default_mode.value}[/]")
        if user_settings.default_mode == GameMode.TIME:
            console.print(f"3. Default Duration: [cyan]{user_settings.default_duration}s[/]")
            default_value_label = "Duration"
            other_option = "4"
        else:
            console.print(f"3. Default Length: [cyan]{user_settings.default_length} words[/]")
            default_value_label = "Length"
            other_option = "4"
        
        console.print(f"4. Change Other Default Value ('{GameMode.WORDS.value if user_settings.default_mode == GameMode.TIME else GameMode.TIME.value}')")
        console.print("5. Set Monkeytype ApeKey (Stored in .env)")
        console.print("6. Reset to Defaults")
        console.print("7. Back to Main Menu")

        choice = Prompt.ask("Choose an option to change", choices=["1", "2", "3", "4", "5", "6", "7"], default="7")

        if choice == '1':
            lang_choices = {str(i+1): lang for i, lang in enumerate(Language)}
            console.print("Select New Default Language:")
            for i, lang in lang_choices.items():
                console.print(f" {i}. {lang.value}")
            lang_choice_num = Prompt.ask("Choose language", choices=list(lang_choices.keys()))
            user_settings.default_language = lang_choices[lang_choice_num]
            user_settings.save()
            console.print(f"[green]Default language set to {user_settings.default_language.value}[/]")
        elif choice == '2':
            mode_choices = {str(i+1): mode for i, mode in enumerate(GameMode)}
            console.print("Select New Default Mode:")
            for i, mode in mode_choices.items():
                console.print(f" {i}. {mode.value}")
            mode_choice_num = Prompt.ask("Choose mode", choices=list(mode_choices.keys()))
            user_settings.default_mode = mode_choices[mode_choice_num]
            user_settings.save()
            console.print(f"[green]Default mode set to {user_settings.default_mode.value}[/]")
        elif choice == '3':
            if user_settings.default_mode == GameMode.TIME:
                user_settings.default_duration = IntPrompt.ask("Enter new default duration (seconds)", default=user_settings.default_duration)
            else:
                user_settings.default_length = IntPrompt.ask("Enter new default length (words)", default=user_settings.default_length)
            user_settings.save()
            console.print(f"[green]Default {default_value_label.lower()} updated.[/]")
        elif choice == '4':
             if user_settings.default_mode != GameMode.TIME:
                 user_settings.default_duration = IntPrompt.ask("Enter new default duration (seconds)", default=user_settings.default_duration)
                 label = "duration"
             else:
                 user_settings.default_length = IntPrompt.ask("Enter new default length (words)", default=user_settings.default_length)
                 label = "length"
             user_settings.save()
             console.print(f"[green]Default {label} updated.[/]")
        elif choice == '5':
            if settings.monkeytype_ape_key:
                console.print(f"Monkeytype ApeKey is currently [green]set[/] (loaded from .env or environment).")
                console.print("To change it, modify your .env file or environment variables.")
            else:
                console.print("Monkeytype ApeKey is [yellow]not set[/].")
                console.print("Please set the [bold]MONKEYTYPE_APE_KEY[/] variable in your .env file or environment.")
            input("Press Enter to continue...")
        elif choice == '6':
            if Confirm.ask("Are you sure you want to reset user settings to defaults?"):
                 user_settings = UserSettings()
                 user_settings.save()
                 console.print("[green]User settings reset to defaults.[/]")
        elif choice == '7':
            break
        else:
            console.print("[red]Invalid choice.[/]")

@app.command()
def stats():
    try:
        asyncio.run(view_stats())
    except ApiClientError as e:
         console.print(f"[bold red]API Error:[/bold red] {e}")
    except Exception as e:
         console.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")

@app.command()
def leaderboard(
    mode: Annotated[
        GameMode,
        typer.Option(help="Leaderboard mode ('time' or 'words')."),
    ] = user_settings.default_mode,
    language: Annotated[
        Language,
        typer.Option("--language", "-l", help="Leaderboard language ('en' or 'id')."),
    ] = user_settings.default_language,
):
    try:
        asyncio.run(view_leaderboard(mode=mode, language=language))
    except ApiClientError as e:
         console.print(f"[bold red]API Error:[/bold red] {e}")
    except Exception as e:
         console.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")

def _call_api_from_menu(func, *args, **kwargs):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console
    ) as progress:
        progress.add_task(description="Connecting to API...", total=None)
        try:
            asyncio.run(func(*args, **kwargs))
        except ApiClientError as e:
            console.print(f"[bold red]API Error:[/bold red] {e}")
        except Exception as e:
            console.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")

async def view_stats():
    console.print("\n[bold]Fetching User Stats & Personal Bests...[/]")
    client = APIClient()
    try:
        stats_response, bests_response = await asyncio.gather(
            client.get_user_stats(),
            client.get_personal_bests()
        )

        if stats_response and stats_response.data:
             ui_stats.display_stats(stats_response.data)
        else:
             console.print(f"[yellow]Could not retrieve user stats. Message: {stats_response.message if stats_response else 'N/A'}[/]")
             
        if bests_response and bests_response.data:
             ui_stats.display_personal_bests(bests_response.data)
        else:
             console.print(f"[yellow]Could not retrieve personal bests. Message: {bests_response.message if bests_response else 'N/A'}[/]")

    finally:
        await client.close()

async def view_leaderboard(mode: GameMode = user_settings.default_mode, language: Language = user_settings.default_language):
    console.print(f"\n[bold]Fetching Leaderboard (Mode: {mode.value}, Lang: {language.value})...[/]")
    client = APIClient()
    try:
        leaderboard_response = await client.get_leaderboard(mode=mode.value, language=language.value)
        
        if leaderboard_response and leaderboard_response.data:
             ui_leaderboard.display_leaderboard(leaderboard_response.data, mode.value, language.value)
        else:
            console.print(f"[yellow]No leaderboard data received. Message: {leaderboard_response.message if leaderboard_response else 'N/A'}[/]")

    finally:
        await client.close()

def view_session_history():
     console.print("\n[bold]Session History[/]")
     if not session_history:
         console.print("No tests completed in this session yet.")
         input("\nPress Enter to return to the menu...") 
         return

     table = Table(title="Current Session Results", show_header=True, header_style="bold cyan")
     table.add_column("Time", style="dim", width=10)
     table.add_column("Mode", width=15)
     table.add_column("WPM", justify="right", style="green")
     table.add_column("Acc %", justify="right", style="blue")
     table.add_column("Raw", justify="right")
     table.add_column("Chars (C/I)", justify="center")

     for i, result in enumerate(reversed(session_history)):
         time_str = f"Test {len(session_history) - i}"
         mode_str = f"{result.mode.value} ({result.config_value})"
         wpm_str = f"{result.wpm:.1f}"
         acc_str = f"{result.accuracy:.1f}"
         raw_str = f"{result.raw_wpm:.1f}"
         chars_str = f"{result.correct_chars}/{result.incorrect_chars}"
         table.add_row(time_str, mode_str, wpm_str, acc_str, raw_str, chars_str)
     
     console.print(table)
     input("\nPress Enter to return to the menu...") 

def show_help():
     console.print("\n[bold]MonkeyTyper CLI Help[/]")
     
     help_text = Text()
     help_text.append("Welcome to MonkeyTyper CLI!\n\n", style="bold cyan")
     help_text.append("Use the interactive menu or run commands directly.\n\n")
     help_text.append("Main Commands:\n", style="bold yellow")
     help_text.append("  start        : Start a new typing test (configurable via options or menu).\n")
     help_text.append("  stats        : View your personal stats (requires ApeKey set in .env).\n")
     help_text.append("  leaderboard  : View public leaderboards.\n")
     help_text.append("  --version    : Show application version.\n")
     help_text.append("  --help       : Show detailed help for commands and options.\n\n")
     
     help_text.append("Menu Options:\n", style="bold yellow")
     help_text.append("  1. Start Test : Configure and begin a typing test.\n")
     help_text.append("  2. View Stats : Fetch and display your stats from Monkeytype.\n")
     help_text.append("  3. Leaderboard: Fetch and display public leaderboards.\n")
     help_text.append("  4. Settings   : Change default test parameters (language, mode, etc.).\n")
     help_text.append("  5. Help       : Display this help message.\n")
     help_text.append("  6. History    : View results from the current session.\n")
     help_text.append("  7. Exit       : Close the application.\n")

     console.print(Panel(help_text, title="Help Summary", border_style="green"))
     input("\nPress Enter to return to the menu...")

if __name__ == "__main__":
    app()
