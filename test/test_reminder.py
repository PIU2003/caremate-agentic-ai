from agents.reminder import ReminderAgent

agent = ReminderAgent()

messages = [
    "Remind me to take my medicine at 8 PM.",
    "Remind me to drink water every hour.",
    "Remind me to visit my doctor tomorrow.",
    "Remind me to exercise every morning.",
]

for message in messages:

    response = agent.run(message)

    print("User :", message)
    print("Reminder Agent :", response)
    print("-" * 50)