"""Reminder time parsing, desktop notifications, and due-reminder processing."""

from __future__ import annotations

import re
from datetime import datetime, timedelta

from database.database import (
    complete_or_reschedule_reminder,
    get_due_reminders,
)


def next_remind_at(hour: int, minute: int = 0, recurrence: str = "none") -> str:
    now = datetime.now()
    due = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if due <= now:
        due += timedelta(days=1)
    return due.strftime("%Y-%m-%d %H:%M:%S")


def parse_time_from_text(text: str) -> tuple[int, int] | None:
    if not text:
        return None

    text = text.strip().lower()

    match = re.search(
        r"\b(\d{1,2})(?::(\d{2}))?\s*(a\.?m\.?|p\.?m\.?)\b",
        text,
    )
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2) or 0)
        meridiem = match.group(3).replace(".", "")
        if hour == 12:
            hour = 0
        if meridiem.startswith("p"):
            hour += 12
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return hour, minute

    match = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", text)
    if match:
        return int(match.group(1)), int(match.group(2))

    match = re.search(r"\bat\s+(\d{1,2})\b", text)
    if match:
        hour = int(match.group(1))
        if 0 <= hour <= 23:
            return hour, 0

    return None


def detect_recurrence(text: str) -> str:
    text = (text or "").lower()
    if any(
        word in text
        for word in (
            "every day",
            "everyday",
            "daily",
            "each day",
            "every morning",
            "every evening",
            "every night",
        )
    ):
        return "daily"
    return "none"


def format_remind_at(remind_at: str | None) -> str:
    if not remind_at:
        return "No time set"
    try:
        dt = datetime.strptime(remind_at, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%b %d, %Y at %I:%M %p")
    except ValueError:
        return remind_at


def show_desktop_notification(title: str, message: str) -> None:
    try:
        from plyer import notification

        notification.notify(
            title=title or "CareMate Reminder",
            message=message or "You have a reminder due.",
            app_name="CareMate AI",
            timeout=10,
        )
        return
    except Exception:
        pass

    try:
        import subprocess

        safe_title = (title or "CareMate Reminder").replace("'", "''")
        safe_message = (message or "You have a reminder due.").replace("'", "''")
        script = f"""
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
$template = @"
<toast>
  <visual>
    <binding template="ToastGeneric">
      <text>{safe_title}</text>
      <text>{safe_message}</text>
    </binding>
  </visual>
</toast>
"@
$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("CareMate AI").Show($toast)
"""
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            check=False,
            capture_output=True,
            timeout=10,
        )
    except Exception:
        pass


def process_due_reminders() -> list[dict]:
    due = get_due_reminders()
    fired = []
    for reminder in due:
        title = reminder["title"] or "CareMate Reminder"
        show_desktop_notification("CareMate Reminder", f"It's time: {title}")
        complete_or_reschedule_reminder(reminder["id"])
        fired.append(reminder)
    return fired
