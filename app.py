from agents.coordinator import CoordinatorAgent
from agents.reminder import ReminderAgent


def main():

    coordinator = CoordinatorAgent()
    reminder = ReminderAgent()

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

        else:

            response = "This agent has not been implemented yet."

        print(f"\nCareMate: {response}")


if __name__ == "__main__":
    main()