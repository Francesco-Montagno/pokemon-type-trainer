from time import perf_counter
from random import choice
from uuid import uuid4
from pathlib import Path
import sys

# Resolve local modules from this file, independent of the launch directory.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from src.database import connect, save_result, fetch_leaderboard
from data.types import TYPES
from src.functions import generate_random_values, generate_question

RANDOM_NAMES = (
    "SparkTrainer", "EmberMaster", "StormTamer", "FrostChampion",
    "ShadowTrainer", "ThunderKeeper", "FlameRanger", "CrystalMaster",
    "WildChallenger", "LeafGuardian", "TideTrainer", "StoneChampion",
    "SwiftTamer", "MoonRanger", "IronMaster", "DawnTrainer",
    "MistKeeper", "BraveChallenger", "SkyGuardian", "StarTamer",
)

st.set_page_config(page_title="Pokémon Type Trainer", page_icon="⚔️", layout="centered")

st.html(f"<style>{(PROJECT_ROOT / 'assets' / 'mobile.css').read_text()}</style>")

st.caption("POKÉMON TRAINING • TYPE MATCHUPS")
st.title(":yellow[Master the matchup.]")
st.write("20 questions. Pick the damage multiplier and sharpen your type knowledge.")


def get_database():
    # Each Streamlit session owns its client; credentials stay on the server.
    if "database_client" not in st.session_state:
        st.session_state.database_client = connect(
            st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_PUBLISHABLE_KEY"]
        )
    return st.session_state.database_client


@st.dialog("🏆 Leaderboard — Top 20", width="large")
def leaderboard_dialog():
    st.caption("Most correct answers first; fastest time breaks ties.")
    try:
        results = fetch_leaderboard(get_database())
    except Exception:
        st.error("Leaderboard unavailable. Please try again later.")
    else:
        if not results:
            st.info("Complete a quiz to appear on the leaderboard.")
        else:
            st.dataframe([
                {"Rank": rank, "Name": result["name"],
                 "Correct answers": result["correct_answers"],
                 "Time (s)": round(result["elapsed_seconds"], 1)}
                for rank, result in enumerate(results, start=1)
            ], hide_index=True, width="stretch")
    if st.button("Close"):
        st.rerun()


def show_leaderboard():
    if st.button("Leaderboard", icon="🏆"):
        leaderboard_dialog()


def start_quiz():
    # Keep preferences separate from widgets, which disappear during the quiz.
    st.session_state.use_random_name = st.session_state.get("random_name", False)
    st.session_state.saved_name = st.session_state.get("name_input", "")
    if st.session_state.use_random_name:
        if "assigned_random_name" not in st.session_state:
            st.session_state.assigned_random_name = choice(RANDOM_NAMES)
        st.session_state.player_name = st.session_state.assigned_random_name
    else:
        name = st.session_state.get("name_input", "").strip()
        if not name:
            return
        st.session_state.player_name = name
    st.session_state.started = True
    st.session_state.score = 0
    st.session_state.answered_count = 0
    st.session_state.answered = False
    st.session_state.history = []
    st.session_state.question = generate_random_values()
    st.session_state.started_at = perf_counter()
    st.session_state.elapsed_seconds = None
    st.session_state.result_recorded = False
    st.session_state.save_attempted = False
    st.session_state.result_id = str(uuid4())


if not st.session_state.get("started", False):
    if "random_name" not in st.session_state:
        st.session_state.random_name = st.session_state.get("use_random_name", False)
    if "name_input" not in st.session_state:
        st.session_state.name_input = st.session_state.get("saved_name", "")
    with st.container(border=True):
        st.subheader("Ready to train?")
        st.write("Answer 20 type matchups. Each correct answer earns one point.")
        random_name = st.checkbox("Random name", key="random_name")
        name = st.text_input(
            "Your name", key="name_input", max_chars=40,
            placeholder="Choose a name for this session", disabled=random_name,
        )
        if random_name:
            if st.session_state.get("assigned_random_name"):
                st.text(f"Trainer: {st.session_state.assigned_random_name}")
            else:
                st.caption("A random trainer name will be generated when you press Play.")
        st.caption("The timer starts when you press Play. Review all your answers at the end.")
        st.button("Play", type="primary", icon="▶️", on_click=start_quiz,
                  disabled=not random_name and not name.strip())
    show_leaderboard()
    st.stop()

if "question" not in st.session_state:
    st.session_state.question = generate_random_values()

# Converti le domande delle sessioni aperte prima della rimozione della difesa.
if len(st.session_state.question) == 3:
    first, second, old_action = st.session_state.question
    st.session_state.question = (first, second) if old_action == 0 else (second, first)

if "score" not in st.session_state:
    st.session_state.score = 0

if "answered_count" not in st.session_state:
    st.session_state.answered_count = 0

if "answered" not in st.session_state:
    st.session_state.answered = False

if "history" not in st.session_state:
    st.session_state.history = []

if "started_at" not in st.session_state:
    st.session_state.started_at = perf_counter()

if "elapsed_seconds" not in st.session_state:
    st.session_state.elapsed_seconds = None

if st.session_state.get("player_name"):
    st.text(f"Trainer: {st.session_state.player_name}")

st.progress(st.session_state.answered_count / 20)
st.caption(f"{st.session_state.answered_count} of 20 questions completed")

if st.session_state.answered_count >= 20:
    if (not st.session_state.get("save_attempted", False)
            and st.session_state.elapsed_seconds is not None):
        st.session_state.save_attempted = True
        if "result_id" not in st.session_state:
            st.session_state.result_id = str(uuid4())
        try:
            save_result(get_database(), {
                "id": st.session_state.result_id,
                "name": st.session_state.get("player_name", "Anonymous"),
                "correct_answers": st.session_state.score,
                "elapsed_seconds": st.session_state.elapsed_seconds,
            })
        except Exception:
            st.session_state.result_recorded = False
        else:
            st.session_state.result_recorded = True
    if st.session_state.get("result_recorded", False):
        st.success("Result saved to the leaderboard.")
    else:
        st.warning("Result not saved. Retry before starting another game.")
        if st.button("Retry saving"):
            st.session_state.save_attempted = False
            st.rerun()
    st.header("Session complete 🏁")
    score_col, accuracy_col, time_col = st.columns(3)
    score_col.metric("Correct answers", f"{st.session_state.score} / 20")
    accuracy_col.metric("Accuracy", f"{st.session_state.score / 20:.0%}")
    elapsed = st.session_state.elapsed_seconds
    time_col.metric("Total time", f"{elapsed:.1f} s" if elapsed is not None else "—")
    if elapsed is not None:
        st.caption(f"Average response time: {elapsed / 20:.1f} seconds per question.")

    show_leaderboard()
    st.divider()
    st.subheader("Review your matchups")
    st.caption("Check the correct multiplier and spot the types to practise next.")
    mistakes_only = st.checkbox("Show only incorrect answers")
    rows = st.session_state.history
    if mistakes_only:
        rows = [row for row in rows if row["Result"] == "❌"]
    if rows:
        st.dataframe(rows, hide_index=True, width="stretch")
    else:
        st.success("No incorrect answers to review.")

    if st.button("Play again", type="primary", icon="🔄"):
        for key in ("started", "score", "answered_count", "answered", "history",
                    "question", "started_at", "elapsed_seconds", "player_name"):
            st.session_state.pop(key, None)
        st.rerun()

    st.stop()

type_1, type_2 = st.session_state.question
correct_answer = generate_question(type_1, type_2)

@st.fragment(run_every="1s")
def show_timer():
    elapsed = st.session_state.elapsed_seconds
    if elapsed is None:
        elapsed = perf_counter() - st.session_state.started_at
    minutes, seconds = divmod(int(elapsed), 60)
    st.metric("Time", f"{minutes:02d}:{seconds:02d}")


with st.container(border=True, key="quiz"):
    heading_col, score_col, timer_col = st.columns([2, 1, 1])
    heading_col.subheader(f"Question {st.session_state.answered_count + 1:02d}")
    score_col.metric("Score", st.session_state.score)
    with timer_col:
        show_timer()
    st.divider()

    col1, col2, col3 = st.columns(3, vertical_alignment="center")
    with col1:
        st.caption("ATTACKING TYPE")
        st.image(str(PROJECT_ROOT / "assets" / "icons" / f"{TYPES[type_1].lower()}.svg"), width=90)
        st.subheader(TYPES[type_1])
    with col2:
        st.markdown("### ⚔️ :red[**ATTACKS**]")
    with col3:
        st.caption("DEFENDING TYPE")
        st.image(str(PROJECT_ROOT / "assets" / "icons" / f"{TYPES[type_2].lower()}.svg"), width=90)
        st.subheader(TYPES[type_2])

    st.divider()
    st.markdown("**How effective is the attack?**")
    selected_answer = None
    answer_columns = st.columns(4)
    choices = [("0×", "⚫", 0), ("½×", "🔴", 0.5),
               ("1×", "⚪", 1), ("2×", "🟢", 2)]
    for column, (label, icon, value) in zip(answer_columns, choices):
        with column:
            if st.button(label, icon=icon, width=80):
                selected_answer = value

st.caption("Choose once to move to the next question. Your time includes pauses.")

if selected_answer is not None and not st.session_state.answered:
    st.session_state.answered = True
    st.session_state.answered_count += 1

    if st.session_state.answered_count == 20:
        st.session_state.elapsed_seconds = perf_counter() - st.session_state.started_at

    st.session_state.history.append({
        "Question": f"{TYPES[type_1]} attacks {TYPES[type_2]}",
        "Your answer": f"{selected_answer:g}×",
        "Correct answer": f"{correct_answer:g}×",
        "Result": "✅" if selected_answer == correct_answer else "❌",
    })

    if selected_answer == correct_answer:
        st.session_state.score += 1

    if st.session_state.answered_count < 20:
        st.session_state.question = generate_random_values()
        st.session_state.answered = False

    st.rerun()
