import json
import pathlib
import sys
from typing import Optional

from pydantic import BaseModel, ValidationError

from monkeytyper_cli.core.models import GameMode
from monkeytyper_cli.core.models import Language

DEFAULT_CONFIG_DIR_NAME = "monkeytyper-cli"
DEFAULT_CONFIG_FILE_NAME = "user_settings.json"


def get_config_path() -> pathlib.Path:
    """Determines the path for the user configuration file."""
    if sys.platform == "win32":
        app_data = pathlib.Path.home() / "AppData" / "Local"
    elif sys.platform == "darwin":
        app_data = pathlib.Path.home() / "Library" / "Application Support"
    else: # Assume Linux/other Unix-like
        app_data = pathlib.Path.home() / ".config"

    config_dir = app_data / DEFAULT_CONFIG_DIR_NAME
    config_dir.mkdir(parents=True, exist_ok=True) # Create dir if it doesn't exist
    return config_dir / DEFAULT_CONFIG_FILE_NAME


class UserSettings(BaseModel):
    """User-specific preferences."""
    default_language: Language = Language.EN
    default_mode: GameMode = GameMode.TIME
    default_duration: int = 30 # Default for time mode
    default_length: int = 25 # Default for words mode

    def save(self):
        """Saves the current settings to the user config file."""
        config_file = get_config_path()
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(self.model_dump_json(indent=4))
        except IOError as e:
            print(f"Error saving user settings to {config_file}: {e}", file=sys.stderr)

    @classmethod
    def load(cls) -> 'UserSettings':
        """Loads settings from the user config file, returning defaults if not found or invalid."""
        config_file = get_config_path()
        if not config_file.exists():
            print(f"User settings file not found at {config_file}. Using defaults.")
            return cls()

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return cls(**data)
        except (IOError, json.JSONDecodeError, ValidationError) as e:
            print(f"Error loading user settings from {config_file}: {e}. Using defaults.", file=sys.stderr)
            return cls()
