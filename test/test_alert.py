from agents.alert import AlertAgent

agent = AlertAgent()

messages = [
    "I have severe chest pain.",
    "My father collapsed.",
    "My grandmother is having difficulty breathing.",
    "Someone is bleeding heavily.",
]

for message in messages:

    response = agent.run(message)

    print("User :", message)
    print("Alert Agent :", response)
    print("-" * 50)