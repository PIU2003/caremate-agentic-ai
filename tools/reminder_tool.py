from database.database import (
    save_reminder,
    get_reminders,
)


class ReminderTool:

    def save(self, request, result):
        save_reminder(request, result)

    def get_all(self):
        return get_reminders()

    def format_reminders(self):

        reminders = self.get_all()

        if not reminders:
            return "You don't have any reminders."

        text = "Here are your reminders:\n\n"

        for i, (request, result) in enumerate(reminders, start=1):
            text += (
            f"{i}.\n"
            f"Request: {request}\n"
            f"Response: {result}\n\n"
        )

        return text