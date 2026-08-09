from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass, field

from .agents import AgentOrchestrator, Plan
from .config import JarvisConfig
from .models import ModelRouter, ModelResponse
from .tools import WebTool

_URL_RE = re.compile(r'https?://[^\s)>"\']+')


@dataclass
class ExecutionResult:
    plan: Plan
    model_response: ModelResponse | None = None
    fetched_pages: dict[str, str] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


class TaskRunner:
    """Executes low-risk tasks Jarvis can perform without side effects."""

    def __init__(self, config: JarvisConfig) -> None:
        self.config = config
        self.orchestrator = AgentOrchestrator()
        self.models = ModelRouter(config.model_endpoints)
        self.web = WebTool()

    async def run(self, goal: str, use_model: bool = True, fetch_web: bool = True) -> ExecutionResult:
        plan = self.orchestrator.create_plan(goal)
        result = ExecutionResult(plan=plan)
        urls = _extract_urls(goal)
        if fetch_web and urls:
            for url in urls:
                try:
                    html = await self.web.fetch(url)
                except Exception as exc:  # network access can fail independently of planning/model work
                    result.notes.append(f"Could not fetch {url}: {exc}")
                    continue
                result.fetched_pages[url] = html[:4000]
                result.notes.append(f"Fetched {url} ({len(html)} characters, first 4000 retained).")
        if use_model:
            prompt = _build_prompt(goal, result)
            try:
                result.model_response = self.models.complete(prompt)
            except Exception as exc:  # model providers may be unconfigured, quota-limited, or unavailable
                result.notes.append(f"Cloud model call skipped/failed: {exc}")
        elif not urls:
            result.notes.append("Execution skipped model calls; only the plan was created.")
        return result


def _extract_urls(text: str) -> list[str]:
    return _URL_RE.findall(text)


def _build_prompt(goal: str, result: ExecutionResult) -> str:
    page_context = "\n\n".join(
        f"URL: {url}\nCONTENT PREVIEW:\n{content}" for url, content in result.fetched_pages.items()
    )
    return (
        "Create a concise, confirmable execution plan for this goal. "
        "Do not claim you completed side effects unless evidence is provided.\n\n"
        f"GOAL:\n{goal}\n\n"
        f"WEB_CONTEXT:\n{page_context or 'No web pages fetched.'}"
    )


def run_sync(goal: str, config: JarvisConfig, use_model: bool = True, fetch_web: bool = True) -> ExecutionResult:
    return asyncio.run(TaskRunner(config).run(goal, use_model=use_model, fetch_web=fetch_web))
