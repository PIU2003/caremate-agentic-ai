from agents.reminder import ReminderAgent
from agents.health import HealthAgent
from agents.conversation import ConversationAgent
from agents.alert import AlertAgent
from agents.summary import SummaryAgent
from src.state import AgentState



class AgentManager:
    """
    Dispatches requests to the correct specialized agent.
    """

    def __init__(self):

        # Shared state
        self.state = AgentState()

        self.agents = {
        "Reminder": ReminderAgent(),
        "Health": HealthAgent(),
        "Conversation": ConversationAgent(),
        "Alert": AlertAgent(),
        "Summary": SummaryAgent(),
        }

    def run(self, agent_name: str, message: str) -> str:

        agent = self.agents.get(agent_name)

        if not agent:
            return "This agent has not been implemented yet."

        response = agent.run(message)

        self.state.chat_history.append(
            {
                 "agent": agent_name,
                 "user": message,
                 "assistant": response,
            }
        )
        
        return response