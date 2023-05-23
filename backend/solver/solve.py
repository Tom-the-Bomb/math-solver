from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias, Any
from functools import cached_property
from contextlib import redirect_stdout
from io import StringIO

from sympy import (
    oo,
    pprint, 
    factor, expand, simplify,
    maximum, minimum,
    solve as s_solve,
    solveset as s_solveset,
)

from .parser import Parser

if TYPE_CHECKING:
    from sympy import Set, Add, Mul, Order, Expr, Basic
    from sympy.core.relational import Relational

    Expression: TypeAlias = Add | Mul | Order | Expr | Basic
    Equation: TypeAlias = Relational | bool

class Solver:
    def __init__(self, /, equation: str) -> None:
        self.parser = Parser()
        self.raw_equation = equation
    
    @cached_property
    def parsed_equation(self, /) -> Equation:
        return self.parser.parse(self.raw_equation).eval()

    @cached_property
    def solution(self, /) -> Set | list[Any]:
        try:
            return s_solveset(self.parsed_equation)
        except Exception as e:
            try:
                return s_solve(self.parsed_equation)
            except Exception as e2:
                raise e from e2
    
    @cached_property
    def parsed_solution(self, /) -> str:
        """prettified and formatted solution"""
        buf = StringIO()
        with redirect_stdout(buf):
            pprint(self.solution)
        return buf.getvalue()
    
    @cached_property
    def factored(self, /) -> Expression:
        """x^2 - 4 -> (x + 2)(x - 2)"""
        return factor(self.parsed_equation)
    
    @cached_property
    def expanded(self, /) -> Expression:
        """(x + 1)(x + 2) -> x^2 + 3x + 2"""
        return expand(self.parsed_equation)
    
    @cached_property
    def simplify(self, /) -> Expression:
        """2x + 1 + 3x + 2 -> 5x + 3"""
        return simplify(self.parsed_equation)
    
    @cached_property
    def max_min(self, /):
        var = self.parser.variables[0]

        max = maximum(self.parsed_equation, var)
        if abs(max) == oo:
            return minimum(self.parsed_equation, var)
        return max