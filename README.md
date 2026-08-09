# Jarvis

Jarvis is a human-confirmed AI operations assistant scaffold. It is designed to coordinate cloud-hosted open-source models, browser automation, file operations, messaging integrations, Google Workspace access, and multi-agent task execution while keeping the operator in control.

> This repository provides the orchestration code and safety boundaries. It does not include credentials, hidden persistence, or unapproved access to devices/accounts.

## Capabilities

- **Web access**: browse online pages, inspect content, and interact with web pages through browser adapters.
- **Computer access**: create, open, and modify files only inside configured allowlisted paths.
- **Communications**: send email and SMS through explicit provider adapters after confirmation.
- **Google Docs / Drive projects**: connect through OAuth-backed Google Workspace adapters.
- **Multi-agent execution**: split work into specialist agents and coordinate their outputs.
- **Cloud model routing**: use remote OpenAI-compatible endpoints for open-source models; no local model runtime is required.
- **Human confirmation**: risky actions are planned, summarized, and confirmed before execution.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
jarvis --goal "Research a topic and draft a plan"
```

## Configuration

Jarvis reads environment variables from the shell or a `.env` file:

| Variable | Purpose |
| --- | --- |
| `JARVIS_MODEL_ENDPOINTS` | JSON array of OpenAI-compatible cloud model endpoints. |
| `JARVIS_WORKSPACE_ROOTS` | Path-separated allowlist of directories Jarvis may access. |
| `JARVIS_REQUIRE_CONFIRMATION` | Keep `true` to require confirmation before side effects. |
| `JARVIS_EMAIL_PROVIDER` | Email adapter name, for example `smtp` or `gmail`. |
| `JARVIS_SMS_PROVIDER` | SMS adapter name, for example `twilio`. |

## Safety model

Jarvis intentionally refuses to bypass account security, exfiltrate secrets, persist without consent, or perform side effects without a confirmation token when confirmation is enabled.
