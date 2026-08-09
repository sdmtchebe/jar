from pathlib import Path

import pytest

from jarvis.agents import AgentOrchestrator, AgentRole
from jarvis.config import JarvisConfig
from jarvis.confirmation import ConfirmationGate
from jarvis.tools import FileTool


def test_orchestrator_creates_specialist_tasks() -> None:
    plan = AgentOrchestrator().create_plan("Browse the web, modify a file, and send email")
    roles = {task.role for task in plan.tasks}
    assert AgentRole.RESEARCHER in roles
    assert AgentRole.FILE_OPERATOR in roles
    assert AgentRole.COMMUNICATOR in roles
    assert plan.questions


def test_file_tool_requires_confirmation(tmp_path: Path) -> None:
    config = JarvisConfig(workspace_roots=[tmp_path])
    confirmations = ConfirmationGate(required=True)
    tool = FileTool(config, confirmations)
    target = tmp_path / "note.txt"

    token = tool.plan_write_text(target, "hello")
    tool.write_text(target, "hello", token)

    assert target.read_text() == "hello"


def test_file_tool_rejects_paths_outside_workspace(tmp_path: Path) -> None:
    config = JarvisConfig(workspace_roots=[tmp_path / "allowed"])
    tool = FileTool(config, ConfirmationGate(required=True))

    with pytest.raises(PermissionError):
        tool.plan_write_text(tmp_path / "blocked.txt", "nope")
