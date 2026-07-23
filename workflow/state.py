from typing import TypedDict

class CareMateState(TypedDict):
    message: str
    selected_agent: str
    response: str

    chat_history: list
    reminders: list
    health_notes: list
    summaries: list