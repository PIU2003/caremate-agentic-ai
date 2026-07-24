from agents.reminder import ReminderAgent

agent = ReminderAgent()

print(agent.detect_intent("Remind me to take medicine at 8 PM"))
print(agent.detect_intent("Show my reminders"))
print(agent.detect_intent("What reminders do I have?"))
print(agent.detect_intent("List all reminders"))