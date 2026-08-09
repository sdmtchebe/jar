from __future__ import annotations

from pathlib import Path

import asyncio
from urllib.request import urlopen

from .config import JarvisConfig
from .confirmation import ConfirmationGate


class FileTool:
    def __init__(self, config: JarvisConfig, confirmations: ConfirmationGate) -> None:
        self.config = config
        self.confirmations = confirmations

    def read_text(self, path: Path) -> str:
        if not self.config.path_allowed(path):
            raise PermissionError(f"Path is outside allowlisted workspace roots: {path}")
        return path.read_text()

    def plan_write_text(self, path: Path, content: str) -> str:
        if not self.config.path_allowed(path):
            raise PermissionError(f"Path is outside allowlisted workspace roots: {path}")
        request = self.confirmations.request(
            "write_file",
            f"Write {len(content)} characters to {path.expanduser().resolve()}",
        )
        return request.token

    def write_text(self, path: Path, content: str, token: str) -> None:
        if self.confirmations.confirm(token) is None:
            raise PermissionError("Missing or invalid confirmation token")
        if not self.config.path_allowed(path):
            raise PermissionError(f"Path is outside allowlisted workspace roots: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


class WebTool:
    async def fetch(self, url: str) -> str:
        def _read() -> str:
            with urlopen(url, timeout=30) as response:
                return response.read().decode("utf-8", errors="replace")

        return await asyncio.to_thread(_read)


class BrowserTool:
    """Placeholder for Playwright/Selenium page interaction adapters."""

    def plan_interaction(self, url: str, description: str, confirmations: ConfirmationGate) -> str:
        request = confirmations.request("browser_interaction", f"Open {url} and {description}")
        return request.token


class CommunicationTool:
    def __init__(self, confirmations: ConfirmationGate) -> None:
        self.confirmations = confirmations

    def plan_email(self, to: str, subject: str, body: str) -> str:
        request = self.confirmations.request(
            "send_email",
            f"Send email to {to!r} with subject {subject!r} and {len(body)} body characters",
        )
        return request.token

    def plan_sms(self, to: str, body: str) -> str:
        request = self.confirmations.request(
            "send_sms",
            f"Send SMS to {to!r} with {len(body)} characters",
        )
        return request.token
