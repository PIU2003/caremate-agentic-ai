"""All CareMate agents (Router, Planning, Reflection, workers)."""

from __future__ import annotations

import json
import re

from src.llm import chat
from src.prompts import (
    ALERT_PROMPT,
    CONVERSATION_PROMPT,
    COORDINATOR_PROMPT,
    HEALTH_PROMPT,
    PLANNER_PROMPT,
    REFLECTION_PROMPT,
    REMINDER_PARSE_PROMPT,
    SUMMARY_PROMPT,
)
from utils.reminders import (
    detect_recurrence,
    next_remind_at,
    parse_time_from_text,
)


class CoordinatorAgent:
    """Router pattern: selects one specialist agent (Groq)."""

    def route(self, message: str) -> str:
        label = chat(
            [
                {"role": "system", "content": COORDINATOR_PROMPT},
                {"role": "user", "content": message},
            ],
            provider="groq",
            temperature=0,
            max_tokens=10,
        )
        return label.strip().split()[0]


class PlannerAgent:
    """Planning pattern: short step plan before Health answers."""

    def plan(self, message: str) -> str:
        return chat(
            [
                {"role": "system", "content": PLANNER_PROMPT},
                {"role": "user", "content": message},
            ],
            provider="openrouter",
            temperature=0.1,
            max_tokens=200,
        )


class ReflectorAgent:
    """Reflection pattern: critique/revise Health drafts."""

    def reflect(self, user_message: str, draft: str, context: str = "") -> str:
        prompt = (
            f"User message:\n{user_message}\n\n"
            f"Knowledge context:\n{context}\n\n"
            f"Draft answer:\n{draft}\n\n"
            "Return the improved final answer only."
        )
        return chat(
            [
                {"role": "system", "content": REFLECTION_PROMPT},
                {"role": "user", "content": prompt},
            ],
            provider="openrouter",
            temperature=0.1,
            max_tokens=250,
        )


_REMINDER_VIEW = (
    "show my reminder",
    "list my reminder",
    "what reminder",
    "my reminders",
    "view my reminder",
)


class ReminderAgent:
    """Reminder create/view (Groq JSON parse + ReminderTool)."""

    def wants_view(self, message: str) -> bool:
        text = message.lower()
        return any(hint in text for hint in _REMINDER_VIEW)

    def parse_reminder(self, message: str) -> dict:
        parsed = {
            "title": message[:50].strip(),
            "time": None,
            "recurrence": detect_recurrence(message),
            "confirmation": "",
            "remind_at": None,
        }
        try:
            raw = chat(
                [
                    {"role": "system", "content": REMINDER_PARSE_PROMPT},
                    {"role": "user", "content": message},
                ],
                provider="groq",
                temperature=0,
                max_tokens=200,
            )
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                parsed["title"] = (data.get("title") or parsed["title"]).strip()
                parsed["time"] = data.get("time")
                recurrence = (data.get("recurrence") or "none").lower()
                parsed["recurrence"] = (
                    "daily" if recurrence == "daily" else "none"
                )
                parsed["confirmation"] = (
                    data.get("confirmation") or ""
                ).strip()
        except Exception:
            pass

        clock = None
        if parsed["time"]:
            clock = parse_time_from_text(str(parsed["time"]))
        if clock is None:
            clock = parse_time_from_text(message)

        if clock is not None:
            hour, minute = clock
            parsed["remind_at"] = next_remind_at(
                hour, minute, parsed["recurrence"]
            )
            parsed["time"] = f"{hour:02d}:{minute:02d}"

        if not parsed["confirmation"]:
            if parsed["remind_at"]:
                when = parsed["time"]
                repeat = (
                    " every day"
                    if parsed["recurrence"] == "daily"
                    else ""
                )
                parsed["confirmation"] = (
                    f"Got it! I'll remind you to {parsed['title']}"
                    f"{repeat} at {when}."
                )
            else:
                parsed["confirmation"] = (
                    f"I've saved your reminder: {parsed['title']}."
                )
        return parsed


_HEALTH_VIEW = (
    "show my health",
    "list my health",
    "health notes",
    "health records",
    "health advice have you",
)


class HealthAgent:
    """Health advice with optional RAG context and plan."""

    def wants_view(self, message: str) -> bool:
        text = message.lower()
        return any(hint in text for hint in _HEALTH_VIEW)

    def run(self, message: str, context: str = "", plan: str = "") -> str:
        user_content = message
        if plan:
            user_content = f"Plan:\n{plan}\n\nUser question:\n{message}"
        if context:
            user_content += (
                "\n\nRetrieved knowledge base context:\n"
                f"{context}\n\n"
                "Use the context when relevant. If context is insufficient, "
                "say so and give cautious general guidance."
            )
        return chat(
            [
                {"role": "system", "content": HEALTH_PROMPT},
                {"role": "user", "content": user_content},
            ],
            provider="openrouter",
            temperature=0.2,
            max_tokens=250,
        )


class ConversationAgent:
    def run(self, message: str) -> str:
        return chat(
            [
                {"role": "system", "content": CONVERSATION_PROMPT},
                {"role": "user", "content": message},
            ],
            provider="openrouter",
            temperature=0.6,
            max_tokens=180,
        )


class AlertAgent:
    def run(self, message: str) -> str:
        return chat(
            [
                {"role": "system", "content": ALERT_PROMPT},
                {"role": "user", "content": message},
            ],
            provider="openrouter",
            temperature=0,
            max_tokens=180,
        )


class SummaryAgent:
    def run(self, message: str) -> str:
        return chat(
            [
                {"role": "system", "content": SUMMARY_PROMPT},
                {"role": "user", "content": message},
            ],
            provider="openrouter",
            temperature=0,
            max_tokens=250,
        )
