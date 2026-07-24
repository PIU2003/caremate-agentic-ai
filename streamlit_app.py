import streamlit as st

from database.database import create_tables
from workflow.graph import graph

create_tables()

st.set_page_config(
    page_title="CareMate AI",
    page_icon="🩺",
    layout="centered"
)

st.title("🩺 CareMate AI")
st.write("An AI-powered multi-agent healthcare assistant.")

if "state" not in st.session_state:
    st.session_state.state = {
        "message": "",
        "selected_agent": "",
        "response": "",
        "chat_history": [],
        "reminders": [],
        "health_notes": [],
        "summaries": [],
    }

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Type your message...")

if user_input:

    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.state["message"] = user_input

    st.session_state.state = graph.invoke(st.session_state.state)

    response = st.session_state.state["response"]
    selected = st.session_state.state["selected_agent"]

    with st.chat_message("assistant"):
        st.markdown(response)
        st.caption(f"Coordinator selected: {selected}")

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )