from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.request import Request, urlopen

from .config import ModelEndpoint


@dataclass(frozen=True)
class ModelResponse:
    provider: str
    model: str
    content: str


class CloudModelClient:
    """Calls OpenAI-compatible cloud model endpoints."""

    def __init__(self, endpoint: ModelEndpoint) -> None:
        self.endpoint = endpoint

    def complete(self, messages: list[dict[str, str]], timeout: int = 60) -> ModelResponse:
        api_key = os.getenv(self.endpoint.api_key_env)
        if not api_key:
            raise RuntimeError(
                f"Missing API key environment variable {self.endpoint.api_key_env} for {self.endpoint.name}"
            )
        url = self.endpoint.base_url.rstrip("/") + "/chat/completions"
        payload = json.dumps({"model": self.endpoint.model, "messages": messages}).encode("utf-8")
        request = Request(
            url,
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        with urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        return ModelResponse(
            provider=self.endpoint.name,
            model=self.endpoint.model,
            content=_extract_content(data),
        )


def _extract_content(data: dict[str, Any]) -> str:
    choices = data.get("choices") or []
    if not choices:
        return json.dumps(data, indent=2)
    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, str):
        return content
    return json.dumps(choices[0], indent=2)


class ModelRouter:
    """Tries configured cloud endpoints in order until one returns a response."""

    def __init__(self, endpoints: list[ModelEndpoint]) -> None:
        self.endpoints = endpoints

    def complete(self, prompt: str) -> ModelResponse:
        if not self.endpoints:
            raise RuntimeError("No cloud model endpoints configured in JARVIS_MODEL_ENDPOINTS")
        messages = [
            {
                "role": "system",
                "content": "You are Jarvis, a careful assistant that plans tasks and asks before side effects.",
            },
            {"role": "user", "content": prompt},
        ]
        errors: list[str] = []
        for endpoint in self.endpoints:
            try:
                return CloudModelClient(endpoint).complete(messages)
            except Exception as exc:  # endpoint failover needs to capture provider-specific failures
                errors.append(f"{endpoint.name}: {exc}")
        raise RuntimeError("All configured model endpoints failed: " + "; ".join(errors))
