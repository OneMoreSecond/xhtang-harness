from __future__ import annotations

import argparse
from collections.abc import Sequence
from typing import cast

from xhtang_harness import __version__

DEFAULT_GOAL = "Show a usable agent harness demo"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xhtang-harness",
        description="Run the xhtang harness demo.",
    )
    parser.add_argument(
        "goal",
        nargs="?",
        default=DEFAULT_GOAL,
        help="Goal to pass through the demo harness.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def render_demo(goal: str) -> str:
    normalized_goal = goal.strip()
    if not normalized_goal:
        raise ValueError("goal must not be empty")

    return "\n".join(
        [
            "xhtang-harness demo",
            f"version: {__version__}",
            f"goal: {normalized_goal}",
            "status: ready",
        ]
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    namespace = parser.parse_args(argv)
    goal = cast(str, namespace.goal)

    try:
        print(render_demo(goal))
    except ValueError as error:
        parser.error(str(error))

    return 0
