from __future__ import annotations

import argparse

from .agents import AgentOrchestrator
from .config import load_config
from .confirmation import ConfirmationGate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Jarvis human-confirmed AI operations assistant")
    parser.add_argument("--goal", required=True, help="Goal Jarvis should plan")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config()
    confirmations = ConfirmationGate(required=config.require_confirmation)
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
    print("\nConfirmation required:")
    print(f"Action: {request.action}")
    print(f"Summary: {request.summary}")
    print(f"Token: {request.token}")
