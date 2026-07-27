"""Tool Use pattern: Reminder, Health, and RAG tools."""

from database.database import (
    get_health_notes,
    get_reminders,
    save_health_note,
    save_reminder,
)
from rag.pipeline import format_context, retrieve
from utils.reminders import format_remind_at


class ReminderTool:
    def save(
        self,
        request,
        result,
        title=None,
        remind_at=None,
        recurrence="none",
    ):
        return save_reminder(
            request=request,
            result=result,
            title=title,
            remind_at=remind_at,
            recurrence=recurrence,
        )

    def format_reminders(self):
        reminders = get_reminders()
        if not reminders:
            return "You don't have any reminders."

        text = "Here are your reminders:\n\n"
        for i, row in enumerate(reminders, start=1):
            _id, title, request, _result, remind_at, recurrence, status = row
            text += (
                f"{i}. {title or request}\n"
                f"   Time: {format_remind_at(remind_at)}\n"
                f"   Repeat: {recurrence or 'none'}\n"
                f"   Status: {status or 'pending'}\n\n"
            )
        return text


class HealthTool:
    def save(self, question, advice):
        save_health_note(question, advice)

    def format_health_notes(self):
        notes = get_health_notes()
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


class RAGTool:
    """Health agent retrieves grounded knowledge passages."""

    def search(self, query: str, top_k: int = 4) -> list[dict]:
        return retrieve(query, top_k=top_k)

    def get_context(self, query: str, top_k: int = 4) -> str:
        return format_context(self.search(query, top_k=top_k))
