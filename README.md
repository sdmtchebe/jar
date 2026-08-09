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

## Dashboard

The GitHub Pages site is a dashboard prototype, not just a landing page. It includes a chat composer, a message history, activity tracking, visible metrics, and local browser storage so you can see what Jarvis planned or recorded during the session. The dashboard still follows the project safety model: it tracks plans and pauses before side effects need confirmation.

## Accessing Jarvis on GitHub vs running it on your Mac

There are two different things you can do with this repository:

1. **View the project on GitHub or GitHub Pages.** This only shows the files or static landing page in a browser. It does not install the `jarvis` command on your Mac.
2. **Run Jarvis on your Mac.** For this, you need a local copy of the repository folder that contains `pyproject.toml`, `.env.example`, and `src/jarvis`. Clone or download the repository first, then run the Quick start commands from inside that folder.

If you are currently at a terminal prompt like `~ %`, you are in your home folder, not necessarily inside the Jarvis project. Run `pwd` to see where you are and `cd path/to/jar` to enter the cloned repository before running `python3 -m pip install -e .`.

## Quick start

Run these commands from the Jarvis project folder (the folder that contains `pyproject.toml`). On macOS, `python` is often not installed as a command name, so use `python3`.

```bash
git clone <your-jarvis-repository-url>
cd jar
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
cp .env.example .env
jarvis --goal "Research a topic and draft a plan"
```

If you already cloned the repository, skip `git clone ...` and `cd` into your existing checkout before running the remaining commands. If `python3` is unavailable, install Python 3.11 or newer first.

### Running Jarvis after setup

The final command in the Quick start is the command that runs Jarvis:

```bash
jarvis --goal "Research a topic and draft a plan"
```

Run each setup command on its own line. If you paste everything as one long line, your shell may treat it as a single broken command. To run setup as one paste safely, join the commands with `&&` so each step must succeed before the next step starts:

```bash
python3 -m venv .venv && \
source .venv/bin/activate && \
python3 -m pip install -e . && \
cp .env.example .env && \
jarvis --goal "Research a topic and draft a plan"
```

After installation, you can run Jarvis again any time from the project folder by activating the virtual environment and running a new goal:

```bash
source .venv/bin/activate
jarvis --goal "Plan my next task"
```

A successful run prints the goal, specialist tasks, clarification questions, and a confirmation token.

### Finding the cloned folder and checking its files

The folder name after `git clone` usually comes from the repository name. For example, cloning a repo named `jar` creates a folder named `jar` unless you choose a different destination name. You can also set the folder name yourself:

```bash
git clone <your-jarvis-repository-url> my-jarvis
cd my-jarvis
```

To confirm you are in the right folder, run:

```bash
pwd
find . -maxdepth 2 -type f | sort
```

You should see project files such as `pyproject.toml`, `README.md`, `.env.example`, `src/jarvis/cli.py`, `src/jarvis/config.py`, and `tests/test_jarvis.py`. If `pyproject.toml` is not listed, you are not in the folder where `python3 -m pip install -e .` should be run.

### Common setup errors

- `zsh: command not found: python`: use `python3` on macOS.
- `source: no such file or directory: .venv/bin/activate`: create the virtual environment first with `python3 -m venv .venv`.
- `does not appear to be a Python project`: you are not in the repository folder that contains `pyproject.toml`; run `cd path/to/jar`.
- `cp: .env.example: No such file or directory`: you are not in the repository folder; run `cd path/to/jar`.
- `zsh: command not found: jarvis`: activate the virtual environment and run `python3 -m pip install -e .` from the repository folder.

## Adding your own API keys and models

Jarvis reads model providers from `.env`. Do **not** paste API keys into GitHub, `README.md`, or committed code. Put the real secret only in your local `.env` file, which is ignored by Git.

1. Copy the example file if you have not already:

```bash
cp .env.example .env
```

2. Open `.env` in a text editor and set `JARVIS_MODEL_ENDPOINTS`. Each endpoint needs:

- `name`: a label you choose, such as `openrouter` or `together`.
- `base_url`: the provider's OpenAI-compatible API base URL.
- `model`: the exact model ID from that provider.
- `api_key_env`: the name of the environment variable that contains the secret API key.

Example:

```bash
JARVIS_MODEL_ENDPOINTS='[{"name":"openrouter","base_url":"https://openrouter.ai/api/v1","model":"meta-llama/llama-3.1-8b-instruct:free","api_key_env":"OPENROUTER_API_KEY"}]'
OPENROUTER_API_KEY="replace-with-your-real-key"
```

3. To use multiple models/providers, add more objects to the JSON array. Jarvis tries them in order:

```bash
JARVIS_MODEL_ENDPOINTS='[{"name":"openrouter","base_url":"https://openrouter.ai/api/v1","model":"model-one","api_key_env":"OPENROUTER_API_KEY"},{"name":"together","base_url":"https://api.together.xyz/v1","model":"model-two","api_key_env":"TOGETHER_API_KEY"}]'
OPENROUTER_API_KEY="replace-with-your-real-key"
TOGETHER_API_KEY="replace-with-your-real-key"
```

4. Verify what Jarvis sees without printing your secret values:

```bash
jarvis --models
```

5. Run Jarvis with the configured model:

```bash
jarvis --goal "Research https://example.com and summarize it" --execute
```

## Terminal dashboard chat

If you do not want to keep typing `jarvis --goal ...`, run Jarvis with no goal:

```bash
jarvis
```

That opens an interactive terminal dashboard where you can chat directly, review recent activity, inspect history, clear the session, and exit. Use `/no-model <task>` inside the dashboard when you want local planning/web-fetch testing without a cloud model call.

GitHub Pages cannot directly access your Mac, local files, terminal, or personal browser because it is just a static web page running inside browser security limits. For computer access and task execution, run the local terminal dashboard from your cloned repository.

## Real model and task execution

Jarvis can call cloud-hosted, OpenAI-compatible model endpoints when you configure them in `.env`. It does not ship with unlimited free compute: every real provider controls its own pricing, quotas, and rate limits. To use free-tier or open-source hosted models, add that provider's endpoint and API-key environment variable to `JARVIS_MODEL_ENDPOINTS`.

Example `.env` shape:

```bash
JARVIS_MODEL_ENDPOINTS='[{"name":"open-router-free","base_url":"https://openrouter.ai/api/v1","model":"some/open-source-model:free","api_key_env":"OPENROUTER_API_KEY"}]'
OPENROUTER_API_KEY="your-provider-key"
```

Run a real low-risk execution with:

```bash
jarvis --goal "Research https://example.com and summarize it" --execute
```

With `--execute`, Jarvis can fetch URLs found in the goal and pass the page preview into the configured cloud model. Side-effect tasks such as writing files, sending messages, or interacting with accounts still require explicit confirmation and provider integrations. If you want to test URL fetching without a model key, run:

```bash
jarvis --goal "Research https://example.com" --execute --no-model
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

## GitHub Pages

This repository includes both a root `index.html` and `docs/index.html` so GitHub Pages works whether the site source is configured as the repository root or the `/docs` folder. A lightweight `404.html` redirects unknown Pages routes back to the landing page.

## Safety model

Jarvis intentionally refuses to bypass account security, exfiltrate secrets, persist without consent, or perform side effects without a confirmation token when confirmation is enabled.
