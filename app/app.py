from time import perf_counter

import streamlit as st

from data.types import TYPES
from src.functions import generate_random_values, generate_question

st.set_page_config(page_title="Pokémon Type Trainer", page_icon="⚔️", layout="centered")

st.caption("POKÉMON TRAINING • TYPE MATCHUPS")
st.title(":yellow[Master the matchup.]")
st.write("20 questions. Pick the damage multiplier and sharpen your type knowledge.")

def start_quiz():
    st.session_state.started = True
    st.session_state.score = 0
    st.session_state.answered_count = 0
    st.session_state.answered = False
    st.session_state.history = []
    st.session_state.question = generate_random_values()
    st.session_state.started_at = perf_counter()
    st.session_state.elapsed_seconds = None


if not st.session_state.get("started", False):
    with st.container(border=True):
        st.subheader("Ready to train?")
        st.write("Answer 20 type matchups. Each correct answer earns one point.")
        st.caption("The timer starts when you press Play. Review all your answers at the end.")
        st.button("Play", type="primary", icon="▶️", on_click=start_quiz)
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

st.progress(st.session_state.answered_count / 20)
st.caption(f"{st.session_state.answered_count} of 20 questions completed")

if st.session_state.answered_count >= 20:
    st.header("Session complete 🏁")
    score_col, accuracy_col, time_col = st.columns(3)
    score_col.metric("Correct answers", f"{st.session_state.score} / 20")
    accuracy_col.metric("Accuracy", f"{st.session_state.score / 20:.0%}")
    elapsed = st.session_state.elapsed_seconds
    time_col.metric("Total time", f"{elapsed:.1f} s" if elapsed is not None else "—")
    if elapsed is not None:
        st.caption(f"Average response time: {elapsed / 20:.1f} seconds per question.")

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
                    "question", "started_at", "elapsed_seconds"):
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


with st.container(border=True):
    heading_col, score_col, timer_col = st.columns([2, 1, 1])
    heading_col.subheader(f"Question {st.session_state.answered_count + 1:02d}")
    score_col.metric("Score", st.session_state.score)
    with timer_col:
        show_timer()
    st.divider()

    col1, col2, col3 = st.columns(3, vertical_alignment="center")
    with col1:
        st.caption("ATTACKING TYPE")
        st.image(f"assets/icons/{TYPES[type_1].lower()}.svg", width=90)
        st.subheader(TYPES[type_1])
    with col2:
        st.markdown("### ⚔️ :red[**ATTACKS**]")
    with col3:
        st.caption("DEFENDING TYPE")
        st.image(f"assets/icons/{TYPES[type_2].lower()}.svg", width=90)
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
