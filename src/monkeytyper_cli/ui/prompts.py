# Placeholder for displaying text prompts (rich) 

from rich.console import Console, Group
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
import time

from monkeytyper_cli.core.models import GameState, TestResult, GameMode

console = Console()

# Store the Live object globally or pass it around?
# For simplicity in this structure, let's keep the logic of *what* to display here,
# and let main.py handle the Live context.

def create_prompt_display(game_state: GameState) -> Panel:
    """Creates a Rich Renderable object representing the current game state."""
    prompt_text = game_state.prompt_text
    user_input_text = game_state.user_input_text # Use processed input text
    error_indices = game_state.error_indices
    current_index = len(user_input_text)

    display = Text()

    for i, char in enumerate(prompt_text):
        style = "dim grey50" # Default style for upcoming text
        display_char = char if char != ' ' else '·' # Use middle dot for space vis

        if i < current_index:
            # Character has been typed or passed
            typed_char = user_input_text[i]
            if i in error_indices:
                # Style the *prompt* character red if the typed one was wrong
                style = "bold red"
                # Optionally display the wrong typed char?
                # display_char = typed_char # This might look confusing
            else:
                style = "bold green" # Correct character
        elif i == current_index:
            # Current character to be typed (cursor position)
            style = "reverse bold blue"
            # If prompt is shorter than input (shouldn't happen with error handling)
            if i >= len(prompt_text):
                 style = "reverse bold red" # Error cursor?

        # Handle cases where user typed more than prompt length
        # These are implicitly handled by `error_indices` added in engine

        display.append(display_char, style=style)

    # Add extra character indicators if user typed past the end
    if len(user_input_text) > len(prompt_text):
         extra_typed = user_input_text[len(prompt_text):]
         for char in extra_typed:
             display.append(char, style="on red") # Indicate extra chars


    # Add Status Information
    status_line = Text()
    elapsed_time = game_state.time_elapsed()

    if game_state.mode == GameMode.TIME:
        time_left = max(0, game_state.config_value - elapsed_time)
        status_line.append(f"Time Left: {time_left:.1f}s", style="yellow")
    elif game_state.mode == GameMode.WORDS:
        # Calculate words typed based on spaces in correct input prefix
        # This is an approximation
        correct_prefix = ""
        for i in range(min(len(user_input_text), len(prompt_text))):
             if i not in error_indices:
                 correct_prefix += user_input_text[i]
             else:
                 break # Stop counting at first error for word count
        words_typed = correct_prefix.count(' ')
        # Add 1 if currently typing a word
        if correct_prefix and not correct_prefix.endswith(' '):
             words_typed += 1
        status_line.append(f"Words: {words_typed}/{game_state.config_value}", style="yellow")

    # Combine prompt and status in a panel
    content = Group(
        display,
        "\n", # Add a newline for separation
        status_line
    )

    return Panel(content, title="MonkeyTyper CLI", border_style="blue")


# This function is obsolete now, main.py will use Live with create_prompt_display
# def display_live_update(game_state: GameState):
#     pass

# Keep display_prompt for potential use outside Live?
# Or rename create_prompt_display to display_prompt if it's the main way?
# Let's keep create_prompt_display as it clearly indicates it *creates* the object.

# Example of how display_prompt might have been used (now handled by Live in main)
# def display_prompt(game_state: GameState):
#     console.clear()
#     console.print(create_prompt_display(game_state))

# We also need a function to display results, likely in a separate ui/results.py
# but let's assume it exists for now. 