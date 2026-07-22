from email import message

from agents import health
from agents import conversation
from agents import alert
from agents.coordinator import CoordinatorAgent
from agents.reminder import ReminderAgent
from agents.health import HealthAgent
from agents.conversation import ConversationAgent
from agents.alert import AlertAgent

def main():

    coordinator = CoordinatorAgent()
    reminder = ReminderAgent()
    health = HealthAgent()
    conversation = ConversationAgent()
    alert = AlertAgent()

    print("=" * 50)
    print("CareMate AI")
    print("=" * 50)

    while True:

        message = input("\nYou: ")

        if message.lower() == "exit":
            break

        selected_agent = coordinator.route(message)

        print(f"\nCoordinator selected: {selected_agent}")

        if selected_agent == "Reminder":

            response = reminder.run(message)

        elif selected_agent == "Health":

            response = health.run(message)

        elif selected_agent == "Conversation":

         response = conversation.run(message)

        elif selected_agent == "Alert":

            response =alert.run(message)

        else:

            response = "This agent has not been implemented yet."
        print(f"\nCareMate: {response}")


if __name__ == "__main__":
    main()