from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class AgentRole(StrEnum):
    PLANNER = "planner"
    RESEARCHER = "researcher"
    BROWSER = "browser"
    FILE_OPERATOR = "file_operator"
    COMMUNICATOR = "communicator"
    GOOGLE_WORKSPACE = "google_workspace"


@dataclass(frozen=True)
class AgentTask:
    role: AgentRole
    objective: str


@dataclass
class Plan:
    goal: str
    tasks: list[AgentTask] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)


class AgentOrchestrator:
    """Splits a user goal into confirmable specialist-agent tasks."""

    def create_plan(self, goal: str) -> Plan:
        lowered = goal.lower()
        tasks = [AgentTask(AgentRole.PLANNER, "Clarify objective, constraints, and confirmation points")]
        if any(word in lowered for word in ("web", "research", "browse", "page")):
            tasks.append(AgentTask(AgentRole.RESEARCHER, "Collect web evidence and cite sources"))
        if any(word in lowered for word in ("file", "create", "modify", "open")):
            tasks.append(AgentTask(AgentRole.FILE_OPERATOR, "Prepare file changes inside allowlisted roots"))
        if any(word in lowered for word in ("email", "sms", "text")):
            tasks.append(AgentTask(AgentRole.COMMUNICATOR, "Draft messages for operator approval"))
        if "google" in lowered or "docs" in lowered or "drive" in lowered:
            tasks.append(AgentTask(AgentRole.GOOGLE_WORKSPACE, "Plan OAuth-backed Google Workspace operations"))
        return Plan(
            goal=goal,
            tasks=tasks,
            questions=[
                "Which accounts and workspace folders are in scope?",
                "Which actions should require confirmation before execution?",
                "Which cloud model providers should be used?",
            ],
        )
