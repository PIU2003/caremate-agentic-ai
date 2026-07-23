from langgraph.graph import StateGraph, START, END

from workflow.state import CareMateState

from workflow.nodes import (
    coordinator_node,
    reminder_node,
    health_node,
    conversation_node,
    alert_node,
    summary_node,
)

builder = StateGraph(CareMateState)

builder.add_node("Coordinator", coordinator_node)
builder.add_node("Reminder", reminder_node)
builder.add_node("Health", health_node)
builder.add_node("Conversation", conversation_node)
builder.add_node("Alert", alert_node)
builder.add_node("Summary", summary_node)


def router(state: CareMateState):

    routes = {
        "Reminder": "Reminder",
        "Health": "Health",
        "Conversation": "Conversation",
        "Alert": "Alert",
        "Summary": "Summary",
    }

    return routes.get(state["selected_agent"], END)


builder.add_edge(START, "Coordinator")

builder.add_conditional_edges(
    "Coordinator",
    router,
)

builder.add_edge("Reminder", END)
builder.add_edge("Health", END)
builder.add_edge("Conversation", END)
builder.add_edge("Alert", END)
builder.add_edge("Summary", END)

graph = builder.compile()