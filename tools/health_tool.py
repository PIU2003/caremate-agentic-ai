from database.database import (
    save_health_note,
    get_health_notes,
)


class HealthTool:

    def save(self, question, advice):
        save_health_note(question, advice)

    def get_all(self):
        return get_health_notes()

    def format_health_notes(self):

        notes = self.get_all()

        if not notes:
            return "No health notes found."

        text = "Here are your health notes:\n\n"

        for i, (question, advice) in enumerate(notes, start=1):
         text += (
                f"{i}.\n"
                f"Question: {question}\n"
                f"Advice: {advice}\n\n"
        )

        return text