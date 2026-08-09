from __future__ import annotations

from dataclasses import dataclass
from secrets import token_hex


@dataclass(frozen=True)
class ConfirmationRequest:
    action: str
    summary: str
    token: str


class ConfirmationGate:
    """Requires explicit operator confirmation before side effects."""

    def __init__(self, required: bool = True) -> None:
        self.required = required
        self._pending: dict[str, ConfirmationRequest] = {}

    def request(self, action: str, summary: str) -> ConfirmationRequest:
        request = ConfirmationRequest(action=action, summary=summary, token=token_hex(8))
        if self.required:
            self._pending[request.token] = request
        return request

    def confirm(self, token: str) -> ConfirmationRequest | None:
        if not self.required:
            return ConfirmationRequest(action="auto-approved", summary="Confirmation disabled", token=token)
        return self._pending.pop(token, None)
