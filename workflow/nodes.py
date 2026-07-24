from workflow import state
from workflow.state import CareMateState

from agents.coordinator import CoordinatorAgent
from agents.reminder import ReminderAgent
from agents.health import HealthAgent
from agents.conversation import ConversationAgent
from agents.alert import AlertAgent
from agents.summary import SummaryAgent
from tools.conversation_tool import ConversationTool
from tools.reminder_tool import ReminderTool
from tools.health_tool import HealthTool
from tools.summary_tool import SummaryTool

coordinator = CoordinatorAgent()
reminder = ReminderAgent()
health = HealthAgent()
conversation = ConversationAgent()
alert = AlertAgent()
summary = SummaryAgent()

conversation_tool = ConversationTool()
reminder_tool = ReminderTool()
health_tool = HealthTool()
summary_tool = SummaryTool()


def coordinator_node(state: CareMateState):
    agent = coordinator.route(state["message"])

    return {
        "selected_agent": agent
    }


def reminder_node(state: CareMateState):

    message = state["message"]

    intent = reminder.detect_intent(message)

    # -----------------------------
    # VIEW REMINDERS
    # -----------------------------
    if intent == "VIEW":

        response = reminder_tool.format_reminders()

        return {
            "response": response,
            "reminders": state["reminders"],
        }

    # -----------------------------
    # CREATE REMINDER
    # -----------------------------
    response = reminder.run(message)

    reminder_tool.save(
        message,
        response
    )

    reminders = state["reminders"].copy()

    reminders.append(
        {
            "request": message,
            "result": response,
        }
    )

    return {
        "response": response,
        "reminders": reminders,
    }

def health_node(state: CareMateState):

    message = state["message"]

    intent = health.detect_intent(message)

    if intent == "VIEW":

        response = health_tool.format_health_notes()

        return {
            "response": response,
            "health_notes": state["health_notes"],
        }

    response = health.run(message)

    health_tool.save(
        message,
        response
    )

    health_notes = state["health_notes"].copy()

    health_notes.append(
        {
            "question": message,
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
    conversation_tool.save(
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
    summary_tool.save(
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