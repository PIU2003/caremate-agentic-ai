from database.database import save_reminder

save_reminder(
    "Test reminder",
    "This is a test."
)

print("Reminder saved!")