from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ModelEndpoint:
    """OpenAI-compatible cloud model endpoint."""

    name: str
    base_url: str
    model: str
    api_key_env: str

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "ModelEndpoint":
        return cls(
            name=str(value["name"]),
            base_url=str(value["base_url"]),
            model=str(value["model"]),
            api_key_env=str(value["api_key_env"]),
        )


@dataclass
class JarvisConfig:
    """Runtime configuration for Jarvis."""

    model_endpoints: list[ModelEndpoint] = field(default_factory=list)
    workspace_roots: list[Path] = field(default_factory=list)
    require_confirmation: bool = True
    email_provider: str = "dry-run"
    sms_provider: str = "dry-run"

    def path_allowed(self, path: Path) -> bool:
        resolved = path.expanduser().resolve()
        return any(resolved == root or root in resolved.parents for root in self.workspace_roots)


def _json_env(name: str, default: Any) -> Any:
    raw = os.getenv(name)
    if not raw:
        return default
    return json.loads(raw)


def load_config() -> JarvisConfig:
    roots = os.getenv("JARVIS_WORKSPACE_ROOTS", os.getcwd()).split(os.pathsep)
    try:
        endpoint_data = _json_env("JARVIS_MODEL_ENDPOINTS", [])
        return JarvisConfig(
            model_endpoints=[ModelEndpoint.from_mapping(item) for item in endpoint_data],
            workspace_roots=[Path(root).expanduser().resolve() for root in roots if root],
            require_confirmation=os.getenv("JARVIS_REQUIRE_CONFIRMATION", "true").lower() == "true",
            email_provider=os.getenv("JARVIS_EMAIL_PROVIDER", "dry-run"),
            sms_provider=os.getenv("JARVIS_SMS_PROVIDER", "dry-run"),
        )
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise SystemExit(f"Invalid Jarvis configuration: {exc}") from exc
