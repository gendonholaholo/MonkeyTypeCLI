# Placeholder for displaying text prompts (rich) 

from rich.console import Console, Group
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
import time

from monkeytyper_cli.core.models import GameState, TestResult, GameMode

console = Console()

# Store the Live object globally or pass it around?
# For simplicity in this structure, let's keep the logic of *what* to display here,
# and let main.py handle the Live context.

def create_prompt_display(game_state: GameState) -> Panel:
    """Creates a Rich Renderable object representing the current game state."""
    prompt_text = game_state.prompt_text
    user_input_text = game_state.user_input_text
    error_indices = game_state.error_indices
    current_index = len(user_input_text)

    # Calculate visible portion of text
    console_width = console.width - 6  # Account for panel borders and padding
    visible_chars = console_width
    
    # Center the text in view
    start_index = max(0, current_index - (visible_chars // 2))
    end_index = min(len(prompt_text), start_index + visible_chars)
    
    # Create the display text
    display = Text()
    
    for i in range(start_index, end_index):
        char = prompt_text[i]
        display_char = '·' if char == ' ' else char
        
        if i < current_index:
            style = "bold green" if i not in error_indices else "bold red"
        elif i == current_index:
            style = "reverse bold blue"
        else:
            style = "dim grey50"
            
        display.append(display_char, style=style)

    # Add status information
    elapsed_time = game_state.time_elapsed()
    status = Text()
    
    if game_state.mode == GameMode.TIME:
        time_left = max(0, game_state.config_value - elapsed_time)
        status.append(f"Time: {time_left:.1f}s", style="yellow")
    else:
        words_typed = user_input_text.count(' ')
        if user_input_text and not user_input_text.endswith(' '):
            words_typed += 1
        status.append(f"Words: {words_typed}/{game_state.config_value}", style="yellow")

    # Create the panel with both display and status
    content = Group(
        display,
        Text(),  # Empty line for padding
        status
    )
    
    return Panel(content, title="MonkeyTyper CLI", border_style="blue", padding=(0, 1))


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