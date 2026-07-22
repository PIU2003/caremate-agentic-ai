from agents.conversation import ConversationAgent

agent = ConversationAgent()

messages = [
    "Hello.",
    "I'm feeling lonely today.",
    "Tell me something positive.",
    "How are you?",
]

for message in messages:

    response = agent.run(message)

    print("User :", message)
    print("Conversation Agent :", response)
    print("-" * 50)