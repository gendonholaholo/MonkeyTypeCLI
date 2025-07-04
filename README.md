# MonkeyTyper CLI

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linter: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Tests: pytest](https://img.shields.io/badge/tested%20with-pytest-0a9edc.svg)](https://docs.pytest.org)

<!-- Add build status badge once CI is set up -->

A command-line interface (CLI) application built with Python to play typing games using data and modes inspired by [Monkeytype](https://monkeytype.com/), leveraging its public API.

---

## Features

- **Typing Games in Terminal:** Play various typing modes directly in your console.
- **Interactive Menu Interface:** Easy-to-navigate menu system for all application features.
- **Multi-language Support:** Practice typing in English and Bahasa Indonesia with randomized word lists.
- **Real-time Feedback:** Instant WPM and accuracy updates (implementation goal).
- **Monkeytype API Integration:**
  - Fetch user statistics (`/users/stats`, `/users/personalBests`).
  - Retrieve public leaderboards (`/leaderboards`).
  - Access user profiles (`/users/{uidOrName}/profile`).
  - _(Note: Fetching specific quotes/prompts needs clarification based on API - may involve `/configuration` or test setup flow)._
- **Rich Display:** Uses `rich` for beautiful and informative terminal output (results, tables).
- **Customizable Modes:** Select game modes (time, words), duration/length, and potentially difficulty or language (depending on API support and implementation).
- **Randomized Text:** Word lists are randomized each time you start a new typing test for varied practice.
- **Performance Metrics:** Clear WPM display after each typing test completion.
- **(Optional) Authentication:** Log in using your Monkeytype ApeKey to fetch personal data and potentially submit results (requires secure local storage).
- **Prompt Source:** Currently, the method for fetching official Monkeytype prompts via API is under investigation (potentially via `/configuration` or other endpoints). Initial versions may use locally generated or sample prompts.

---

## Technology Stack

- **Language:** Python (>=3.10)
- **CLI Framework:** [Typer](https://typer.tiangolo.com/) (based on Click)
- **HTTP Client:** [httpx](https://www.python-httpx.org/) (async-ready)
- **Terminal UI:** [rich](https://rich.readthedocs.io/en/stable/)
- **Testing:** [pytest](https://docs.pytest.org/)
- **Linting/Formatting:** [ruff](https://github.com/astral-sh/ruff) & [black](https://github.com/psf/black)
- **Packaging/Dependencies:** [Poetry](https://python-poetry.org/) or standard `pip` with `venv`.

---

## Project Structure

The project follows a modular structure for better organization and maintainability:

```
monkeytyper-cli/
├── src/
│   ├── monkeytyper_cli/
│   │   ├── __init__.py
│   │   ├── api/             # Modules for API interaction
│   │   │   ├── __init__.py
│   │   │   ├── client.py    # HTTP client setup (httpx)
│   │   │   ├── models.py    # Pydantic models for API responses
│   │   │   └── endpoints/   # Specific endpoint functions
│   │   │       ├── __init__.py
│   │   │       └── ...
│   │   ├── core/            # Core game logic
│   │   │   ├── __init__.py
│   │   │   ├── engine.py    # Typing test logic (WPM, accuracy)
│   │   │   └── models.py    # Game state, results models
│   │   ├── ui/              # User interface elements (rich)
│   │   │   ├── __init__.py
│   │   │   ├── menu.py      # Interactive menu system
│   │   │   ├── prompts.py   # Displaying text prompts
│   │   │   └── results.py   # Displaying results tables/panels
│   │   ├── data/            # Word lists and text resources
│   │   │   ├── __init__.py
│   │   │   ├── english.py   # English word lists
│   │   │   └── indonesian.py # Bahasa Indonesia word lists
│   │   ├── auth/            # Authentication handling (ApeKey)
│   │   │   ├── __init__.py
│   │   │   └── storage.py   # Secure key storage (keyring/env)
│   │   ├── config/          # Configuration management
│   │   │   ├── __init__.py
│   │   │   └── settings.py  # App settings, constants
│   │   └── main.py          # Typer CLI application definition
│   └── __main__.py          # Allows running with `python -m monkeytyper_cli`
├── tests/                   # Pytest tests
│   ├── __init__.py
│   ├── api/
│   ├── core/
│   └── ui/
├── docs/                    # Documentation files
│   ├── readme.md            # This file
│   └── ...
├── .env.example             # Example environment variables
├── .gitignore
├── pyproject.toml           # Project metadata, dependencies (Poetry)
└── README.md                # Link to docs/readme.md or copy
```

---

## Getting Started

### Prerequisites

- Python >= 3.10
- `pip` and `venv` (or `poetry`)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/gendonholaholo/MonkeyTypeCLI.git
    cd MonkeyTypeCLI
    ```

2.  **Set up a virtual environment:**

    - **Using `venv`:**
      ```bash
      python -m venv .venv
      source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
      pip install -r requirements.txt # Or pip install . if using pyproject.toml setup
      ```
    - **Using `poetry`:**
      ```bash
      poetry install
      poetry shell
      ```

3.  **(Optional) Configure API Key:**
    - Obtain an `ApeKey` from your Monkeytype account settings.
    - Create a `.env` file (copy from `.env.example`).
    - Add your key: `MONKEYTYPE_APE_KEY="YOUR_ACTUAL_APE_KEY"`
    - The application will attempt to load this key for authenticated requests. Secure storage mechanisms (`keyring`) might be implemented later.

### Usage

Run the main application using:

```bash
python -m monkeytyper_cli
```

Or, if installed via `pip install .` or `poetry install`:

```bash
monkeytyper-cli
```

This will launch the interactive menu interface where you can select from the following options:

1. Start Typing Test
2. View Stats
3. View Leaderboard
4. Settings
5. Help
6. Exit

**Alternative Command-Line Usage:**

- **Start a default typing test:**
  ```bash
  monkeytyper-cli start
  ```
- **Start a time-based test (e.g., 60 seconds):**
  ```bash
  monkeytyper-cli start --mode time --duration 60
  ```
- **Start a word-based test (e.g., 50 words):**
  ```bash
  monkeytyper-cli start --mode words --length 50
  ```
- **Start a test with Bahasa Indonesia words:**
  ```bash
  monkeytyper-cli start --language indonesian
  ```
- **View your personal bests (requires auth):**
  ```bash
  monkeytyper-cli stats pbs --mode time --duration 60
  ```
- **View leaderboard:**
  ```bash
  monkeytyper-cli leaderboard --mode time --duration 60 --language english
  ```

Run `monkeytyper-cli --help` for a full list of commands and options.

---

## Testing

Tests are written using `pytest`.

1.  Make sure development dependencies are installed (usually handled by `poetry install --with dev` or a `requirements-dev.txt`).
2.  Run tests from the project root directory:
    ```bash
    pytest
    ```

---

## Monkeytype API Integration

This application interacts with the official [Monkeytype API v2](https://api.monkeytype.com/docs).

**Base URL:** `https://api.monkeytype.com/`

**Authentication:**
Requests requiring user data use an `ApeKey` passed in the `Authorization` header:
`Authorization: ApeKey YOUR_APE_KEY`

**Rate Limiting:**
Be mindful of API rate limits (generally 30 requests/minute per IP/key). The application should handle potential `429 Too Many Requests` errors gracefully.

**Key Endpoints Used (Planned):**

- `GET /users/stats`: Fetch general typing statistics for the authenticated user.
- `GET /users/personalBests`: Get detailed personal bests for specific modes.
- `GET /users/{uidOrName}/profile`: Retrieve public user profile data.
- `GET /leaderboards`: Fetch all-time leaderboards for specific modes/languages.
- `GET /results/last`: Get the last test result for the authenticated user.
- `GET /configuration`: Potentially used to understand available modes, languages, or test parameters. _(Actual method for getting test prompts needs confirmation)_.

_(Detailed request/response examples for each endpoint could be added here or in separate API documentation.)_

---

## Contributing

Contributions are welcome! Please follow standard Fork & Pull Request workflows. Ensure tests pass and code adheres to linting/formatting standards (`ruff`, `black`).

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## License

Distributed under the MIT License. See `LICENSE` file for more information.

---

## Acknowledgements

- [Monkeytype](https://monkeytype.com/) for the awesome typing platform and API.
- [Typer](https://typer.tiangolo.com/)
- [httpx](https://www.python-httpx.org/)

---

## ⚠️ Known Limitations

- **Prompt Source:** As mentioned in Features, fetching official, dynamically generated prompts like the main Monkeytype site is not yet implemented due to API endpoint uncertainty.
- **Result Submission:** Submitting test results back to Monkeytype is not currently supported (pending API capability confirmation).
- **Real-time Feedback:** While a goal, sophisticated real-time feedback during the test might be limited in the initial versions.

---

## ✅ Definition of Done (v1.0 Target)

- Interactive menu interface implemented and functional.
- Core features functional: `start` (with time/word modes), `stats pbs` (auth), `leaderboard`.
- Support for English and Bahasa Indonesia word lists with randomization.
- Clear WPM display after test completion.
- Stable execution on major platforms (Linux, macOS, Windows).
- Acceptable performance for core typing loop.
- Clear error handling for common API issues (4xx/5xx errors, rate limits).
- Reasonable unit test coverage for core logic (>70%).
- Complete CLI help messages (`--help`).
- Comprehensive README documentation.

![image](https://github.com/user-attachments/assets/5a4356c6-da85-4890-b08a-2873bf6619d6)

![image](https://github.com/user-attachments/assets/eb66251e-9c97-41c8-bea0-1e47fe82f0e8)

---

## 🛣️ Roadmap (Planned Features)

- **Interactive Menu Enhancement:** Improve the menu system with more options and customization.
- **Additional Languages:** Support for more languages beyond English and Bahasa Indonesia.
- **Word List Expansion:** Expand word lists for more varied typing practice.
- **Difficulty Levels:** Add options for beginner, intermediate, and advanced word lists.
- **Official Prompt Integration:** Utilize the correct API endpoint for prompts once identified.
- **Result Submission:** Allow submitting results to Monkeytype (if API supports it).
- **More Game Modes:** Support for additional modes like 'quote' or 'zen'.
- **Advanced Configuration:** Options for punctuation, numbers, etc.
- **Local Result History:** Track user progress locally.
- **Enhanced UI:** More detailed real-time feedback, custom themes.
- **Secure Key Storage:** Use `keyring` for ApeKey management.
- **PyPI Packaging:** Publish for easy `pip install`.

---
