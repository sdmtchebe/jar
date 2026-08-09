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


def test_load_config_reads_dotenv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("JARVIS_REQUIRE_CONFIRMATION", raising=False)
    monkeypatch.delenv("JARVIS_WORKSPACE_ROOTS", raising=False)
    (tmp_path / ".env").write_text(
        "JARVIS_REQUIRE_CONFIRMATION=false\n"
        f"JARVIS_WORKSPACE_ROOTS={tmp_path}\n"
    )

    from jarvis.config import load_config

    config = load_config()

    assert config.require_confirmation is False
    assert config.workspace_roots == [tmp_path.resolve()]


def test_runner_fetches_url_without_model(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from jarvis import runner

    async def fake_fetch(url: str) -> str:
        return "<html><title>Example</title></html>"

    monkeypatch.setattr(runner.WebTool, "fetch", lambda self, url: fake_fetch(url))
    config = JarvisConfig(workspace_roots=[tmp_path])

    result = runner.run_sync("Research https://example.com", config, use_model=False)

    assert result.fetched_pages["https://example.com"] == "<html><title>Example</title></html>"
    assert result.notes == ["Fetched https://example.com (35 characters, first 4000 retained)."]


def test_extracts_openai_compatible_model_content() -> None:
    from jarvis.models import _extract_content

    payload = {"choices": [{"message": {"content": "model answer"}}]}

    assert _extract_content(payload) == "model answer"
