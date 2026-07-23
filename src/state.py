from dataclasses import dataclass, field


@dataclass
class AgentState:
    """
    Shared state used by all agents.
    """

    chat_history: list = field(default_factory=list)
    reminders: list = field(default_factory=list)
    health_notes: list = field(default_factory=list)
    summaries: list = field(default_factory=list)