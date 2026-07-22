from agents.health import HealthAgent

agent = HealthAgent()

messages = [
    "My blood pressure is 150 over 95.",
    "How can I reduce my blood sugar?",
    "What foods are good for my heart?",
    "Is walking every day healthy?",
]

for message in messages:

    response = agent.run(message)

    print("User :", message)
    print("Health Agent :", response)
    print("-" * 50)