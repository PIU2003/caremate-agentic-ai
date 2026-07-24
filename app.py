from database.database import create_tables
from workflow.graph import graph

create_tables()


def main():

    print("=" * 50)
    print("CareMate AI")
    print("=" * 50)

    state = {
        "message": "",
        "selected_agent": "",
        "response": "",
        "chat_history": [],
        "reminders": [],
        "health_notes": [],
        "summaries": [],
    }

    while True:

        message = input("\nYou: ")

        if message.lower() == "exit":
            break

        state["message"] = message

        state = graph.invoke(state)

        print(f"\nCoordinator selected: {state['selected_agent']}")
        print(f"\nCareMate: {state['response']}")


if __name__ == "__main__":
    main()