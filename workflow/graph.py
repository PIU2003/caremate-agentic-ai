"""LangGraph workflow: state, nodes, and compiled graph."""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from agents.agents import (
    AlertAgent,
    ConversationAgent,
    CoordinatorAgent,
    HealthAgent,
    PlannerAgent,
    ReflectorAgent,
    ReminderAgent,
    SummaryAgent,
)
from database.database import save_summary
from tools.tools import HealthTool, RAGTool, ReminderTool


class CareMateState(TypedDict):
    message: str
    selected_agent: str
    response: str
    chat_history: list
    plan: str
    retrieved_context: str
    draft_response: str


coordinator = CoordinatorAgent()
reminder = ReminderAgent()
health = HealthAgent()
conversation = ConversationAgent()
alert = AlertAgent()
summary = SummaryAgent()
planner = PlannerAgent()
reflector = ReflectorAgent()

reminder_tool = ReminderTool()
health_tool = HealthTool()
rag_tool = RAGTool()


def coordinator_node(state: CareMateState):
    return {"selected_agent": coordinator.route(state["message"])}


def reminder_node(state: CareMateState):
    message = state["message"]
    if reminder.wants_view(message):
        return {"response": reminder_tool.format_reminders()}

    parsed = reminder.parse_reminder(message)
    response = parsed["confirmation"]
    reminder_tool.save(
        request=message,
        result=response,
        title=parsed["title"],
        remind_at=parsed["remind_at"],
        recurrence=parsed["recurrence"],
    )
    return {"response": response}


def health_node(state: CareMateState):
    """Health path: Planning → RAG tool use → HealthAgent → Reflection."""
    message = state["message"]
    if health.wants_view(message):
        return {
            "response": health_tool.format_health_notes(),
            "plan": "",
            "retrieved_context": "",
            "draft_response": "",
        }

    plan = planner.plan(message)
    retrieved_context = rag_tool.get_context(message, top_k=4)
    draft = health.run(message, context=retrieved_context, plan=plan)
    response = reflector.reflect(
        user_message=message,
        draft=draft,
        context=retrieved_context,
    )
    health_tool.save(message, response)
    return {
        "response": response,
        "plan": plan,
        "retrieved_context": retrieved_context,
        "draft_response": draft,
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
    chat_history = history.copy()
    chat_history.append(
        {"user": state["message"], "assistant": response}
    )
    return {"response": response, "chat_history": chat_history}


def alert_node(state: CareMateState):
    response = alert.run(state["message"])
    return {"response": response, "draft_response": response}


def summary_node(state: CareMateState):
    response = summary.run(state["message"])
    save_summary(state["message"], response)
    return {"response": response}


def router(state: CareMateState):
    routes = {
        "Reminder": "Reminder",
        "Health": "Health",
        "Conversation": "Conversation",
        "Alert": "Alert",
        "Summary": "Summary",
    }
    return routes.get(state["selected_agent"], END)


builder = StateGraph(CareMateState)
builder.add_node("Coordinator", coordinator_node)
builder.add_node("Reminder", reminder_node)
builder.add_node("Health", health_node)
builder.add_node("Conversation", conversation_node)
builder.add_node("Alert", alert_node)
builder.add_node("Summary", summary_node)
builder.add_edge(START, "Coordinator")
builder.add_conditional_edges("Coordinator", router)
builder.add_edge("Reminder", END)
builder.add_edge("Health", END)
builder.add_edge("Conversation", END)
builder.add_edge("Alert", END)
builder.add_edge("Summary", END)

graph = builder.compile()
