# Pokémon Type Trainer

A Streamlit quiz to practise type effectiveness across all 18 Pokémon types.

This is the **offline / local version**: the app runs on your computer and is accessed through your browser. No account, external service, or online database is required. An internet connection is needed to install dependencies; once installed, the quiz and icons work locally.

Prefer to play online without installing anything? Open [Pokémon Type Trainer](https://pokemon-type-trainer.streamlit.app), with a shared leaderboard and no registration required. The online version is developed on the `feature/online` branch.

## How it works

- Each session contains 20 random questions: the first type attacks the second.
- Choose the damage multiplier: **0×, ½×, 1×, or 2×**.
- Each correct answer earns one point. Clicking an answer automatically advances to the next question.
- The final summary shows your score, accuracy, total time, average time, and answer history. You can filter the history to review only incorrect answers.
- **Play again** resets the score, timer, and history and returns to the welcome screen. Press **Play** when you are ready to start a new session.

The quiz covers single-type effectiveness only: dual types, STAB, abilities, held items, and other modifiers are not included.

## Requirements

- **Python 3.11** (the version used to verify this project).
- A modern browser.
- **Streamlit 1.63.0**, pinned in `requirements.txt`. Its dependencies are installed automatically.

`random` and `time` are included in Python's standard library and do not require separate installation.

## Installation and startup

Download or clone the project, then open a terminal in the `pokemon` project root: the directory containing `requirements.txt`, `app`, `assets`, `data`, and `src`.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app/app.py
```

### Windows (PowerShell)

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app/app.py
```

### Using an existing Conda environment

Activate your Python 3.11 environment, then install the dependencies and start the app:

```bash
conda create -n pokemon python=3.11
conda activate pokemon
python -m pip install -r requirements.txt
python -m streamlit run app/app.py
```

You do not need to create a `.venv` environment as well if you use Conda.

Streamlit prints the local address in the terminal, usually [http://localhost:8501](http://localhost:8501). Open it in your browser. To stop the server, press **Ctrl+C** in the terminal.

**Always run the command from the project root:** imports and relative icon paths depend on this location. Do not launch the app with `python app/app.py`.

## Result storage

In this version, results are stored only in the Streamlit session (`st.session_state`). They are not saved to disk or a database, and there is no shared leaderboard. Refreshing the browser or starting a new session may reset them; **Play again** clears the previous session's history.

## Project structure

```text
pokemon/
├── .streamlit/config.toml   # Native theme: colors and fonts
├── app/app.py              # Interface, session state, scoring, and timer
├── assets/icons/           # All 18 SVG icons and their license
├── data/types.py           # Type index → name mapping
├── data/type_chart.py      # Matrix: attacking row, defending column
├── src/functions.py        # Random type selection and correct answer
├── requirements.txt
└── README.md
```

## Troubleshooting

- **`No module named 'data'`**: make sure you are in the project root and use `python -m streamlit run app/app.py`.
- **Icon not found**: check that the files are in `assets/icons/`, with lowercase names such as `fire.svg`.
- **An old function is still loaded after editing**: stop Streamlit with Ctrl+C and run the startup command again.
- **Theme not updated**: restart Streamlit and check that the app's theme is selected in the interface.

## License

The project code is licensed under the [MIT License](LICENSE).
Third-party icons retain their original copyright notice and [MIT License](assets/icons/LICENSE).

## Acknowledgements

Thanks to **James Watkins ([partywhale on GitHub](https://github.com/partywhale))** for the Pokémon type SVG icons:

- Original repository: [partywhale/pokemon-type-icons](https://github.com/partywhale/pokemon-type-icons).
- The author distributes the icons under the **MIT License**. The original copyright notice and license text are included in [assets/icons/LICENSE](assets/icons/LICENSE).

The license above applies to the icon set. This is an unofficial learning project and is not affiliated with The Pokémon Company, Nintendo, Game Freak, or Creatures.
