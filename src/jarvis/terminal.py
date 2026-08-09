from __future__ import annotations

from .config import JarvisConfig
from .session import ChatSession


HELP = """Available commands:
  /help              Show this help message.
  /activity          Show the latest activity entries.
  /history           Show the chat history.
  /no-model <task>   Run planning/web fetching without calling a cloud model.
  /clear             Clear this terminal session.
  /exit              Quit Jarvis.

Type any normal message to ask Jarvis to plan/execute low-risk work.
"""


def run_terminal_dashboard(config: JarvisConfig) -> None:
    session = ChatSession(config=config)
    print(session.render_dashboard())
    print("Jarvis is ready. Type your request and press Enter.")
    while True:
        try:
            message = input("\nYou > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nJarvis session closed.")
            return
        if not message:
            continue
        if message in {"/exit", "exit", "quit", "/quit"}:
            print("Jarvis session closed.")
            return
        if message == "/help":
            print(HELP)
            continue
        if message == "/activity":
            print(session.render_dashboard())
            continue
        if message == "/history":
            _print_history(session)
            continue
        if message == "/clear":
            session.clear()
            print(session.render_dashboard())
            continue
        use_model = True
        if message.startswith("/no-model "):
            use_model = False
            message = message.removeprefix("/no-model ").strip()
            if not message:
                print("Write a task after /no-model.")
                continue
        print("\nJarvis is working...")
        reply = session.submit(message, use_model=use_model)
        print("\nJarvis >")
        print(reply)
        print("\n" + session.render_dashboard())


def _print_history(session: ChatSession) -> None:
    if not session.history:
        print("No chat history yet.")
        return
    for speaker, text in session.history:
        print(f"\n{speaker.title()} >")
        print(text)
