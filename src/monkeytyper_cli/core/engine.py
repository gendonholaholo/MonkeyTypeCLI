import time
from typing import Tuple, List
import random
import pathlib
import sys # For backspace character check

from .models import GameState, TestResult, TestState, GameMode

DATA_DIR = pathlib.Path(__file__).parent.parent / "data"

WORD_LIST_CACHE = {}


def load_word_list(language: str) -> List[str]:
    """Loads and caches word list for a given language."""
    if language in WORD_LIST_CACHE:
        return WORD_LIST_CACHE[language]

    file_path = DATA_DIR / f"{language}_words.txt"
    if not file_path.is_file():
        print(f"Warning: Word list for '{language}' not found. Falling back to English.", file=sys.stderr)
        language = 'en' # Set language to en for cache key consistency
        file_path = DATA_DIR / f"{language}_words.txt"
        if not file_path.is_file():
            raise FileNotFoundError("Default English word list (en_words.txt) not found in data directory.")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f if line.strip()]
        if not words:
            raise ValueError(f"Word list file '{file_path}' is empty.")
        WORD_LIST_CACHE[language] = words
        return words
    except Exception as e:
        raise IOError(f"Error loading word list from '{file_path}': {e}") from e


def generate_prompt_text(word_list: List[str], mode: GameMode, config_value: int) -> str:
    """Generates the prompt string based on the mode and config."""
    if not word_list:
        return "error loading words"

    num_available_words = len(word_list)
    if mode == GameMode.WORDS:
        num_words_to_select = min(config_value, num_available_words)
        selected_words = random.sample(word_list, k=num_words_to_select)
    elif mode == GameMode.TIME:
        num_words_to_select = min(200, num_available_words) # Adjust sample size as needed
        selected_words = random.choices(word_list, k=num_words_to_select)
    else:
        selected_words = random.sample(word_list, k=min(50, num_available_words)) # Fallback

    return " ".join(selected_words)


def start_game(mode: GameMode, config_value: int, language: str) -> GameState:
    """Initializes the game state for a new test including language support."""
    try:
        words = load_word_list(language)
    except (FileNotFoundError, IOError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        words = ["error", "loading", "wordlist"]

    prompt = generate_prompt_text(words, mode, config_value)
    return GameState(
        prompt_text=prompt,
        mode=mode,
        config_value=config_value,
        state=TestState.NOT_STARTED,
        language=language # Store language in state if needed later
    )

BACKSPACE_CHAR = '\x7f' if sys.platform != 'win32' else '\b'

def process_input(game_state: GameState, char: str) -> None:
    """Processes a single character input from the user, including backspace."""
    if game_state.state == TestState.FINISHED or game_state.is_finished():
        return

    if game_state.state == TestState.NOT_STARTED:
        if char != BACKSPACE_CHAR:
            game_state.state = TestState.RUNNING
            game_state.start_time = time.monotonic()
        else:
            return # Ignore backspace before starting

    current_input_index = len(game_state.user_input_chars)

    if char == BACKSPACE_CHAR:
        if current_input_index > 0:
            game_state.user_input_chars.pop()
            removed_char_index = current_input_index - 1
            game_state.error_indices.discard(removed_char_index)
            game_state.current_char_index_overall = len(game_state.user_input_chars)
            game_state.user_input_text = "".join(game_state.user_input_chars)
            game_state.current_word_index = game_state.user_input_text.count(' ')

    elif char.isprintable() or char == ' ':
        game_state.user_input_chars.append(char)
        game_state.user_input_text = "".join(game_state.user_input_chars)
        game_state.total_typed_entries += 1
        current_input_index = len(game_state.user_input_chars) - 1 # Index of char just added

        if current_input_index < len(game_state.prompt_text):
            expected_char = game_state.prompt_text[current_input_index]
            if char != expected_char:
                game_state.error_indices.add(current_input_index)
            else:
                game_state.error_indices.discard(current_input_index)
        else:
            game_state.error_indices.add(current_input_index)

        game_state.current_char_index_overall = len(game_state.user_input_chars)
        if char == ' ':
            game_state.current_word_index += 1

    if game_state.is_finished() and game_state.state != TestState.FINISHED:
        finish_game(game_state)

def finish_game(game_state: GameState):
    """Sets the game state to finished and records end time."""
    if game_state.state != TestState.FINISHED:
        game_state.state = TestState.FINISHED
        if game_state.end_time is None:
            game_state.end_time = time.monotonic()
        if game_state.start_time is None:
            game_state.start_time = game_state.end_time


def calculate_results(game_state: GameState) -> TestResult:
    """Calculates the final test results from the game state."""
    if game_state.state != TestState.FINISHED and game_state.is_finished():
        finish_game(game_state)

    if game_state.state != TestState.FINISHED:
        return TestResult(mode=game_state.mode, config_value=game_state.config_value)

    elapsed_time = game_state.time_elapsed()
    if elapsed_time <= 0:
        return TestResult(mode=game_state.mode, config_value=game_state.config_value)

    correct_chars = 0
    incorrect_chars = 0
    num_chars_to_compare = min(len(game_state.user_input_text), len(game_state.prompt_text))

    for i in range(num_chars_to_compare):
        if game_state.user_input_text[i] == game_state.prompt_text[i]:
            correct_chars += 1
        else:
            incorrect_chars += 1

    extra_chars = len(game_state.user_input_text) - len(game_state.prompt_text)
    if extra_chars > 0:
        incorrect_chars += extra_chars

    game_state.correct_chars_count = correct_chars
    game_state.incorrect_chars_count = incorrect_chars # Update state for consistency? Or just use local vars?

    correct_wpm = (correct_chars / 5) / (elapsed_time / 60)

    raw_wpm = (game_state.total_typed_entries / 5) / (elapsed_time / 60)

    total_compared_chars = correct_chars + incorrect_chars
    accuracy = (correct_chars / total_compared_chars * 100) if total_compared_chars > 0 else 0.0

    if game_state.mode == GameMode.TIME:
        total_expected_chars = len(game_state.user_input_text)
    elif game_state.mode == GameMode.WORDS:
        words_to_consider = game_state.prompt_words[:game_state.config_value]
        if len(words_to_consider) < game_state.config_value:
             print(f"Warning: Generated prompt has only {len(words_to_consider)} words, less than requested {game_state.config_value}.", file=sys.stderr)
        total_expected_chars = len(" ".join(words_to_consider))
    else:
        total_expected_chars = len(game_state.prompt_text) # Fallback

    return TestResult(
        wpm=correct_wpm,
        raw_wpm=raw_wpm,
        accuracy=accuracy,
        correct_chars=correct_chars,
        incorrect_chars=incorrect_chars,
        total_chars=total_expected_chars, # Represents the length of the test portion completed
        time_elapsed_seconds=elapsed_time,
        mode=game_state.mode,
        config_value=game_state.config_value,
    ) 
