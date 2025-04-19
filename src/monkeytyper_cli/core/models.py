from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Any, Optional
import time

class GameMode(Enum):
    TIME = "time"
    WORDS = "words"

class Language(str, Enum):
    EN = "en"
    ID = "id"


class TestState(Enum):
    NOT_STARTED = "not_started"
    RUNNING = "running"
    FINISHED = "finished"


class TestResult(BaseModel):
    wpm: float = 0.0
    raw_wpm: float = 0.0 # WPM based on all typed entries, including errors
    accuracy: float = 0.0
    correct_chars: int = 0
    incorrect_chars: int = 0
    total_chars: int = 0 # Total expected chars in the completed part
    time_elapsed_seconds: float = 0.0
    mode: GameMode
    config_value: int # Duration in seconds for time mode, word count for words mode


class GameState(BaseModel):
    prompt_text: str
    prompt_words: List[str] = Field(default_factory=list)
    user_input_text: str = ""
    user_input_chars: List[str] = Field(default_factory=list) # Store individual typed chars
    error_indices: set[int] = Field(default_factory=set) # Indices of errors in user_input_chars

    current_word_index: int = 0
    current_char_index_overall: int = 0 # Index in the overall prompt string

    start_time: float | None = None
    end_time: float | None = None
    state: TestState = TestState.NOT_STARTED

    correct_chars_count: int = 0
    incorrect_chars_count: int = 0
    total_typed_entries: int = 0 # All valid character keystrokes (non-backspace)

    # Configuration
    mode: GameMode
    config_value: int # Duration or word count
    language: Optional[Language] = None # Store language, make optional for safety

    def model_post_init(self, __context: Any) -> None:
        if self.prompt_text:
            self.prompt_words = self.prompt_text.split(' ')

    def current_prompt_word(self) -> str | None:
        if 0 <= self.current_word_index < len(self.prompt_words):
            return self.prompt_words[self.current_word_index]
        return None

    def time_elapsed(self) -> float:
        """Calculates elapsed time since the test started."""
        if self.start_time is None:
            return 0.0
        current_time = self.end_time or time.monotonic()
        return current_time - self.start_time

    def is_finished(self) -> bool:
        """Check if the game should finish based on mode."""
        if self.state == TestState.FINISHED:
            return True
        if self.mode == GameMode.TIME:
            return self.time_elapsed() >= self.config_value
        elif self.mode == GameMode.WORDS:
            # Finish when the start of the configured word count is reached
            return self.current_word_index >= self.config_value
        return False 
