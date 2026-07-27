from datetime import datetime, timedelta
from pathlib import Path

import streamlit as st

from database.database import (
    create_chat_session,
    create_tables,
    delete_chat_session,
    delete_reminder,
    get_chat_messages,
    get_chat_sessions,
    get_reminders,
    save_chat_message,
    save_reminder,
)
from utils.reminders import format_remind_at, next_remind_at, process_due_reminders
from workflow.graph import graph

st.set_page_config(
    page_title="CareMate AI",
    page_icon="🩺",
    layout="wide",
)

create_tables()

# -----------------------------
# Session State
# -----------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

if "state" not in st.session_state:
    st.session_state.state = {
        "message": "",
        "selected_agent": "",
        "response": "",
        "chat_history": [],
        "plan": "",
        "retrieved_context": "",
        "draft_response": "",
    }

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = ""

if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = None

if "fired_alerts" not in st.session_state:
    st.session_state.fired_alerts = []


def reset_conversation():
    st.session_state.messages = []
    st.session_state.pending_question = ""
    st.session_state.state = {
        "message": "",
        "selected_agent": "",
        "response": "",
        "chat_history": [],
        "plan": "",
        "retrieved_context": "",
        "draft_response": "",
    }


def start_new_conversation():
    reset_conversation()
    st.session_state.active_chat_id = create_chat_session()


def load_conversation(session_id):
    reset_conversation()
    st.session_state.active_chat_id = session_id
    st.session_state.messages = [
        {"role": role, "content": content, "agent": agent}
        for role, content, agent in get_chat_messages(session_id)
    ]

    user_message = None
    for message in st.session_state.messages:
        if message["role"] == "user":
            user_message = message["content"]
        elif user_message:
            st.session_state.state["chat_history"].append(
                {"user": user_message, "assistant": message["content"]}
            )
            user_message = None


@st.dialog("➕ Create Reminder")
def create_reminder_popup():
    title = st.text_input(
        "What should I remind you about?",
        placeholder="Take blood pressure medicine",
    )
    remind_time = st.time_input(
        "Time",
        value=datetime.now().replace(hour=20, minute=0, second=0).time(),
    )
    recurrence = st.selectbox("Repeat", ["Once", "Every day"])

    if st.button("Save Reminder", type="primary", use_container_width=True):
        if not title.strip():
            st.warning("Please enter a reminder title.")
            return

        remind_at = next_remind_at(remind_time.hour, remind_time.minute)
        recurrence_value = "daily" if recurrence == "Every day" else "none"
        confirmation = (
            f"Got it! I'll remind you to {title.strip()}"
            f"{' every day' if recurrence_value == 'daily' else ''}"
            f" at {remind_time.strftime('%I:%M %p')}."
        )

        save_reminder(
            request=title.strip(),
            result=confirmation,
            title=title.strip(),
            remind_at=remind_at,
            recurrence=recurrence_value,
        )
        st.success("Reminder saved!")
        st.rerun()


@st.fragment(run_every=timedelta(minutes=1))
def reminder_watchdog():
    fired = process_due_reminders()
    if not fired:
        return

    for reminder in fired:
        title = reminder["title"] or "Reminder"
        st.toast(f"⏰ {title}", icon="💊")
        st.session_state.fired_alerts = (
            st.session_state.fired_alerts + [title]
        )[-5:]

    st.rerun()


if st.session_state.active_chat_id is None and st.session_state.messages:
    st.session_state.active_chat_id = create_chat_session()
    for message in st.session_state.messages:
        save_chat_message(
            st.session_state.active_chat_id,
            message["role"],
            message["content"],
            message.get("agent"),
        )


IMAGE_PATH = Path(__file__).parent / "images" / "grandparents.png.webp.webp"

# Check due reminders every minute while the app is open
reminder_watchdog()

# Show recent reminder popups / alerts
if st.session_state.fired_alerts:
    for alert_title in st.session_state.fired_alerts:
        st.warning(f"💊 Reminder due: **{alert_title}**", icon="⏰")
    if st.button("Dismiss alerts"):
        st.session_state.fired_alerts = []
        st.rerun()

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:

    st.title("🩺 CareMate AI")

    if IMAGE_PATH.exists():
        st.image(str(IMAGE_PATH), use_container_width=True)

    st.divider()

    if st.button("⌂ Home", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()

    if st.button(
        "💬 Start Conversation",
        type="primary",
        use_container_width=True,
    ):
        start_new_conversation()
        st.session_state.page = "chat"
        st.rerun()

    if st.button("➕ New Reminder", use_container_width=True):
        create_reminder_popup()

    st.subheader("⏰ Upcoming Reminders")
    upcoming = get_reminders()
    if not upcoming:
        st.caption("No upcoming reminders.")
    else:
        for row in upcoming[:5]:
            reminder_id, title, _request, _result, remind_at, recurrence, status = row
            label = title or "Reminder"
            st.markdown(
                f"**{label}**  \n"
                f"{format_remind_at(remind_at)}  \n"
                f"`{recurrence or 'none'}` · `{status or 'pending'}`"
            )
            if st.button(
                "Delete",
                key=f"del_rem_{reminder_id}",
                use_container_width=True,
            ):
                delete_reminder(reminder_id)
                st.rerun()

    st.subheader("📚 Chat History")

    chat_sessions = get_chat_sessions()

    if not chat_sessions:
        st.caption("No conversations yet.")
    else:
        for session_id, title in chat_sessions:
            open_col, delete_col = st.columns([5, 1])

            with open_col:
                if st.button(
                    title,
                    key=f"history_{session_id}",
                    use_container_width=True,
                ):
                    load_conversation(session_id)
                    st.session_state.page = "chat"
                    st.rerun()

            with delete_col:
                if st.button(
                    "🗑️",
                    key=f"delete_{session_id}",
                    use_container_width=True,
                    help="Delete chat",
                ):
                    delete_chat_session(session_id)
                    if st.session_state.active_chat_id == session_id:
                        reset_conversation()
                        st.session_state.active_chat_id = None
                        st.session_state.page = "home"
                    st.rerun()

# ======================================================
# HOME DASHBOARD
# ======================================================

if st.session_state.page == "home":
    st.title("🩺 CareMate AI")

    st.caption(
        "Your Intelligent Healthcare Companion for Elderly Care"
    )

    st.markdown("## Suggested Questions")

    col1, col2 = st.columns(2)

    questions = [
        "❤️ I have a headache",
        "💊 Remind me to take my blood pressure medicine every day at 8 PM",
        "📋 Show my reminders",
        "📝 Show my health notes",
        "😴 I can't sleep",
        "😊 I feel stressed",
        "🍎 Give me healthy diet advice",
        "🚶 Recommend light exercise",
    ]

    for i, q in enumerate(questions):

        if i % 2 == 0:

            if col1.button(q, use_container_width=True):
                start_new_conversation()
                st.session_state.pending_question = q
                st.session_state.page = "chat"
                st.rerun()

        else:

            if col2.button(q, use_container_width=True):
                start_new_conversation()
                st.session_state.pending_question = q
                st.session_state.page = "chat"
                st.rerun()

# ======================================================
# CHAT PAGE
# ======================================================

elif st.session_state.page == "chat":
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and "agent" in msg:
                st.info(f"🤖 Selected Agent: {msg['agent']}")

    user_input = st.session_state.pending_question or st.chat_input(
        "Ask CareMate AI..."
    )
    st.session_state.pending_question = ""

    if user_input:
        if st.session_state.active_chat_id is None:
            st.session_state.active_chat_id = create_chat_session()

        user_message = {"role": "user", "content": user_input}
        st.session_state.messages.append(user_message)
        save_chat_message(st.session_state.active_chat_id, **user_message)
        with st.chat_message("user"):
            st.markdown(user_input)

        st.session_state.state["message"] = user_input
        with st.spinner("CareMate AI is thinking..."):
            st.session_state.state = graph.invoke(st.session_state.state)

        response = st.session_state.state["response"]
        selected = st.session_state.state["selected_agent"]
        with st.chat_message("assistant"):
            st.markdown(response)
            st.info(f"🤖 Selected Agent: {selected}")
            if selected == "Health" and st.session_state.state.get("plan"):
                with st.expander("Planning steps"):
                    st.markdown(st.session_state.state["plan"])
            if selected == "Health" and st.session_state.state.get("retrieved_context"):
                with st.expander("Retrieved RAG context"):
                    st.markdown(st.session_state.state["retrieved_context"])

        assistant_message = {
            "role": "assistant",
            "content": response,
            "agent": selected,
        }
        st.session_state.messages.append(assistant_message)
        save_chat_message(st.session_state.active_chat_id, **assistant_message)
        st.rerun()

    st.markdown("---")
    st.caption("Developed using Streamlit • LangGraph • Groq • SQLite")
