from email import message

from agents import health
from agents import conversation
from agents import alert
from agents.coordinator import CoordinatorAgent
from agents.manager import AgentManager

def main():

    coordinator = CoordinatorAgent()
    manager = AgentManager()

    print("=" * 50)
    print("CareMate AI")
    print("=" * 50)

    while True:

        message = input("\nYou: ")

        if message.lower() == "exit":
            break

        selected_agent = coordinator.route(message)

        print(f"\nCoordinator selected: {selected_agent}")

        response = manager.run(selected_agent, message)

        
        print(f"\nCareMate: {response}")


if __name__ == "__main__":
    main()