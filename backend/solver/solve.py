from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

from sympy import Eq, solve as solve_eq

from .parser import Parser

if TYPE_CHECKING:
    from sympy.core.relational import Relational

    Equation: TypeAlias = Relational | bool

class Solver:
    def __init__(self, /) -> None:
        self.parser = Parser()

    def parse_equation(self, equation: str) -> Equation:
        return self.parser.parse(equation).eval()

    def solve(self, equation: str) -> set:
        return solve_eq(self.parse_equation(equation)) # type: ignore