from agents.reminder import ReminderAgent
from agents.health import HealthAgent
from agents.conversation import ConversationAgent
from agents.alert import AlertAgent
from agents.summary import SummaryAgent


class AgentManager:
    """
    Dispatches requests to the correct specialized agent.
    """

    def __init__(self):

        self.agents = {
            "Reminder": ReminderAgent(),
            "Health": HealthAgent(),
            "Conversation": ConversationAgent(),
            "Alert": AlertAgent(),
            "Summary": SummaryAgent(),
        }

    def run(self, agent_name: str, message: str) -> str:

        agent = self.agents.get(agent_name)

        if agent:

            return agent.run(message)

        return "This agent has not been implemented yet."