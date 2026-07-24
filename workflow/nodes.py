from workflow.state import CareMateState

from agents.coordinator import CoordinatorAgent
from agents.reminder import ReminderAgent
from agents.health import HealthAgent
from agents.conversation import ConversationAgent
from agents.alert import AlertAgent
from agents.summary import SummaryAgent
from database.database import (
    save_conversation,
    save_reminder,
    save_health_note,
    save_summary,
    get_reminders,
)

coordinator = CoordinatorAgent()
reminder = ReminderAgent()
health = HealthAgent()
conversation = ConversationAgent()
alert = AlertAgent()
summary = SummaryAgent()


def coordinator_node(state: CareMateState):
    agent = coordinator.route(state["message"])

    return {
        "selected_agent": agent
    }


def reminder_node(state: CareMateState):

    response = reminder.run(state["message"])

    print(">>> save_reminder() called")


    save_reminder(
        state["message"],
        response
    )

    reminders = state["reminders"].copy()

    reminders.append(
        {
            "request": state["message"],
            "result": response,
        }
    )

    return {
        "response": response,
        "reminders": reminders,
    }


def health_node(state: CareMateState):

    response = health.run(state["message"])
    save_health_note(
        state["message"],
        response
    )

    health_notes = state["health_notes"].copy()

    health_notes.append(
        {
            "question": state["message"],
            "advice": response,
        }
    )

    return {
        "response": response,
        "health_notes": health_notes,
    }


def conversation_node(state: CareMateState):

    history = state["chat_history"]

    context = ""

    if history:
        context = "Previous conversation:\n"

        for item in history:
            context += (
                f'User: {item["user"]}\n'
                f'Assistant: {item["assistant"]}\n'
            )

    message = context + "\nCurrent user message:\n" + state["message"]

    response = conversation.run(message)
    save_conversation(
        state["message"],
        response
    )

    chat_history = history.copy()

    chat_history.append(
        {
            "user": state["message"],
            "assistant": response,
        }
    )

    return {
        "response": response,
        "chat_history": chat_history,
    }


def alert_node(state: CareMateState):
    return {
        "response": alert.run(state["message"])
    }


def summary_node(state: CareMateState):

    response = summary.run(state["message"])
    save_summary(
        state["message"],
        response
    )
    summaries = state["summaries"].copy()

    summaries.append(
        {
            "input": state["message"],
            "summary": response,
        }
    )

    return {
        "response": response,
        "summaries": summaries,
    }