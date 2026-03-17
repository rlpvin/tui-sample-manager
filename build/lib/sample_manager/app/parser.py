from dataclasses import dataclass
from typing import List


@dataclass
class Command:
    name: str
    args: List[str]


def parse_command(input_line: str) -> Command:
    """
    Parse raw user input into command + arguments.
    """

    tokens = input_line.strip().split()

    if not tokens:
        raise ValueError("Empty command")

    name = tokens[0]
    args = tokens[1:]

    return Command(name=name, args=args)
