# Pokémon Type Trainer

A Streamlit quiz to practise type effectiveness across all 18 Pokémon types.

This is the **online version**, developed on the `feature/online` branch, with a shared Supabase leaderboard. Players choose a name or use a random trainer name without creating an account.

**Play online on Streamlit Community Cloud:** [link to be added after deployment].

## Online and offline versions

- **`feature/online`**: online version with result storage in Supabase and a shared top-20 leaderboard. Once deployed, you can play directly in your browser without installing anything.
- **`main`**: offline / local version, with no Supabase configuration or shared leaderboard. An internet connection is needed to install dependencies; the quiz then runs locally.

To use the offline version, run these commands from your local clone with your Python environment activated:

```bash
git checkout main
python -m pip install -r requirements.txt
python -m streamlit run app/app.py
```

Follow the README on `main` for the full offline setup. To return to the online branch:

```bash
git checkout feature/online
```

The instructions below describe running and configuring the **online version** locally.

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

## Run the online version locally

Clone the project, select `feature/online` with `git checkout feature/online`, then open a terminal in the `pokemon` project root: the directory containing `requirements.txt`, `app`, `assets`, `data`, and `src`. Configure Supabase using the instructions below to enable saving results and loading the shared leaderboard.

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

Run the commands above from the project root. Local modules and icons are resolved relative to the app file, including on Streamlit Community Cloud. Do not launch the app with `python app/app.py`.

## Result storage

Completed games are saved to Supabase. Opening the leaderboard fetches the best 20 results by score, time, creation date, and ID. Names can repeat: each row represents a game. A stable UUID prevents duplicate submissions when retrying a request whose response was lost.

### Supabase setup

1. Create `public.results` with the schema below if it does not already exist. If you already created it, skip this step.

```sql
CREATE TABLE public.results (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL CHECK (char_length(trim(name)) BETWEEN 1 AND 40),
    correct_answers integer NOT NULL CHECK (correct_answers BETWEEN 0 AND 20),
    elapsed_seconds double precision NOT NULL
        CHECK (elapsed_seconds >= 0 AND elapsed_seconds < 'Infinity'::double precision),
    created_at timestamptz NOT NULL DEFAULT now()
);
```

2. Run `sql/results_access.sql` in Supabase SQL Editor. `GRANT` permits reading and inserting into this table; RLS policies permit those operations on its rows. No update or delete permission is granted. The index supports leaderboard ordering.
3. Copy `.streamlit/secrets.example.toml` to `.streamlit/secrets.toml` and fill in your project URL and publishable key from Supabase. The real secrets file is ignored by Git. Do not use a service-role or secret key: this setup uses the restricted `anon` role.
4. Install `requirements.txt` and restart Streamlit. On Streamlit Community Cloud, enter the same TOML values in the app's Secrets settings and use `app/app.py` as the entry point.
5. Complete a game, check the row in Supabase Table Editor, and open Leaderboard. Open another browser session to verify the shared ranking.

These policies allow anonymous reading and insertion of results. Anyone with the project URL and publishable key can submit results directly; this is a casual leaderboard, not an anti-cheat system. The key stays in Streamlit's server-side secrets.

If configuration or networking fails, the quiz remains playable and shows a save warning. Use **Retry saving** before starting another game; unsaved results are not durable across a new game or browser session. A failed leaderboard query displays an error rather than an empty ranking.

Database calls live in `src/database.py`: `insert` sends a result; `select`, `order`, and `limit` implement the top-20 query. Credentials and the client stay on the Streamlit server. Query results are not cached.


## Project structure

```text
pokemon/
├── .streamlit/config.toml   # Native theme: colors and fonts
├── .streamlit/secrets.example.toml # Example Supabase configuration
├── app/app.py              # Interface, session state, scoring, and timer
├── assets/icons/           # All 18 SVG icons and their license
├── data/types.py           # Type index → name mapping
├── data/type_chart.py      # Matrix: attacking row, defending column
├── sql/results_access.sql # Database permissions, RLS policies, and index
├── src/database.py        # Supabase result saving and leaderboard queries
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
