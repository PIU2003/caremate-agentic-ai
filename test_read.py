from database.database import (
    get_conversations,
    get_reminders,
    get_health_notes,
    get_summaries,
)

print("Conversations:")
print(get_conversations())

print("\nReminders:")
print(get_reminders())

print("\nHealth Notes:")
print(get_health_notes())

print("\nSummaries:")
print(get_summaries())