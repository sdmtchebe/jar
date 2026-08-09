from __future__ import annotations

import argparse

from .agents import AgentOrchestrator
from .config import load_config
from .confirmation import ConfirmationGate
from .runner import run_sync
from .terminal import run_terminal_dashboard


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Jarvis human-confirmed AI operations assistant")
    parser.add_argument("--goal", help="Goal Jarvis should plan. Omit this to open the terminal dashboard.")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Run low-risk execution: fetch URLs in the goal and call configured cloud model endpoints.",
    )
    parser.add_argument(
        "--no-model",
        action="store_true",
        help="Skip cloud model calls and only create a plan/fetch URLs.",
    )
    parser.add_argument(
        "--chat",
        action="store_true",
        help="Open the interactive terminal dashboard even if other flags are present.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config()

    if args.chat or not args.goal:
        run_terminal_dashboard(config)
        return

    confirmations = ConfirmationGate(required=config.require_confirmation)

    if args.execute:
        result = run_sync(args.goal, config, use_model=not args.no_model)
        plan = result.plan
    else:
        result = None
        plan = AgentOrchestrator().create_plan(args.goal)

    request = confirmations.request(
        "execute_plan",
        f"Execute {len(plan.tasks)} planned specialist-agent tasks for goal: {plan.goal}",
    )

    print(f"Goal: {plan.goal}")
    print("\nSpecialist tasks:")
    for index, task in enumerate(plan.tasks, start=1):
        print(f"{index}. {task.role}: {task.objective}")
    print("\nQuestions before execution:")
    for question in plan.questions:
        print(f"- {question}")

    if result is not None:
        print("\nExecution notes:")
        for note in result.notes or ["No low-risk actions were available to execute."]:
            print(f"- {note}")
        if result.model_response is not None:
            print("\nCloud model response:")
            print(f"Provider: {result.model_response.provider}")
            print(f"Model: {result.model_response.model}")
            print(result.model_response.content)

    print("\nConfirmation required:")
    print(f"Action: {request.action}")
    print(f"Summary: {request.summary}")
    print(f"Token: {request.token}")


if __name__ == "__main__":
    main()
