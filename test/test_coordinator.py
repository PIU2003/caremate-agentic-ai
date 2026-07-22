from agents.coordinator import CoordinatorAgent

coordinator = CoordinatorAgent()

messages = [
    "Remind me to take my medicine at 8 PM.",
    "My blood pressure is 180 over 120.",
    "I'm feeling lonely today.",
    "Give me today's health summary.",
]

for message in messages:
    agent = coordinator.route(message)

    print(f"User : {message}")
    print(f"Agent: {agent}")
    print("-" * 40)