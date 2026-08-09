from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from .config import JarvisConfig
from .runner import run_sync


@dataclass(frozen=True)
class Activity:
    timestamp: str
    title: str
    detail: str


@dataclass
class ChatSession:
    config: JarvisConfig
    history: list[tuple[str, str]] = field(default_factory=list)
    activities: list[Activity] = field(default_factory=list)

    def submit(self, message: str, use_model: bool = True) -> str:
        self.history.append(("you", message))
        self.activities.insert(0, _activity("User message", message))
        result = run_sync(message, self.config, use_model=use_model)
        lines: list[str] = ["Plan:"]
        for index, task in enumerate(result.plan.tasks, start=1):
            lines.append(f"{index}. {task.role}: {task.objective}")
        if result.notes:
            lines.append("\nActivity:")
            lines.extend(f"- {note}" for note in result.notes)
        if result.model_response is not None:
            lines.append("\nModel response:")
            lines.append(result.model_response.content)
        else:
            lines.append("\nNo model response yet. Configure JARVIS_MODEL_ENDPOINTS or use /no-model for local planning/fetching.")
        reply = "\n".join(lines)
        self.history.append(("jarvis", reply))
        self.activities.insert(0, _activity("Jarvis response", "Created plan and recorded execution notes."))
        return reply

    def render_dashboard(self) -> str:
        recent = self.activities[:6]
        activity_lines = [f"[{item.timestamp}] {item.title}: {item.detail}" for item in recent]
        if not activity_lines:
            activity_lines = ["No activity yet. Type a message to start."]
        return "\n".join(
            [
                "=" * 72,
                "JARVIS TERMINAL DASHBOARD",
                f"Messages: {len(self.history)} | Activities: {len(self.activities)}",
                "Commands: /help, /activity, /history, /no-model <task>, /clear, /exit",
                "-" * 72,
                "Recent activity:",
                *activity_lines,
                "=" * 72,
            ]
        )

    def clear(self) -> None:
        self.history.clear()
        self.activities.clear()
        self.activities.append(_activity("Session cleared", "History and activity were cleared."))


def _activity(title: str, detail: str) -> Activity:
    return Activity(
        timestamp=datetime.now().strftime("%H:%M:%S"),
        title=title,
        detail=detail[:220],
    )
