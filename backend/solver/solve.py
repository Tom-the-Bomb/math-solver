from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias, Optional, Any
from functools import cached_property
from contextlib import redirect_stdout
from io import StringIO
import warnings

from sympy import (
    oo,
    Reals,
    pprint,
    Interval,
    latex as s_latex,
    factor, expand, simplify,
    maximum, minimum,
    solve as s_solve,
    solveset as s_solveset,
)
from sympy.calculus.util import function_range, continuous_domain

from .parser import Parser, Constants, Functions
from .ast import DefinedFunction
from .exceptions import *

if TYPE_CHECKING:
    from sympy import Set, Add, Mul, Order, Expr, Basic
    from sympy.core.relational import Relational
    from sympy import Number

    Expression: TypeAlias = Add | Mul | Order | Expr | Basic
    Equation: TypeAlias = Relational | bool

class Solver:
    def __init__(
        self, /,
        equation: str,
        *,
        domain: Optional[str] = None,
        solve_for: Optional[str] = None,
        functions: Optional[list[str]] = None,
        constants: Optional[Constants] = None,
        parser: Optional[Parser] = None,
    ) -> None:
        self.raw_equation = equation

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')

            parsed_functions = {}
            if functions:
                for f in functions:
                    parsed = Parser(constants=constants).parse(f)
                    if not isinstance(parsed, DefinedFunction):
                        raise NotAFunction(f)
                    parsed_functions.update(parsed.eval())
            self.parser = parser or Parser(
                constants=constants,
                functions=parsed_functions,
            )
            self.parsed_equation

            self._domain = Parser().parse(domain).eval() if domain else None
        self.solve_for = solve_for

        self.kwargs = {}
        if self._domain is not None:
            self.kwargs['domain'] = self._domain
        if self.solve_for:
            self.kwargs['symbol'] = self.solve_for

    @cached_property
    def parsed_equation(self, /) -> Equation | Interval | Functions:
        return self.parser.parse(self.raw_equation).eval()

    @cached_property
    def solution(self, /) -> Set | list[Any]:
        try:
            return s_solveset(self.parsed_equation, **self.kwargs)
        except Exception as e:
            try:
                return s_solve(self.parsed_equation, **self.kwargs)
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
    def latex_solution(self, /) -> str:
        """latex solution"""
        return s_latex(self.solution)

    @cached_property
    def factored(self, /) -> Expression:
        """x^2 - 4 -> (x + 2)(x - 2)"""
        return factor(self.parsed_equation)

    @cached_property
    def expanded(self, /) -> Expression:
        """(x + 1)(x + 2) -> x^2 + 3x + 2"""
        return expand(self.parsed_equation)

    @cached_property
    def simplified(self, /) -> Expression:
        """2x + 1 + 3x + 2 -> 5x + 3"""
        return simplify(self.parsed_equation)

    @cached_property
    def max_min(self, /) -> dict[str, Number]:
        result = {}
        kwargs = {
            'symbol': self.parser.variables[0].eval(),
            **self.kwargs
        }

        try:
            if abs(maxima := maximum(self.parsed_equation.lhs, **kwargs)) != oo: # type: ignore
                result['max'] = maxima
        except (ValueError, IndexError) as e:
            raise CantGetProperty('maxima') from e
        try:
            if abs(minima := minimum(self.parsed_equation.lhs, **kwargs)) != oo: # type: ignore
                result['min'] = minima
        except (ValueError, IndexError) as e:
            raise CantGetProperty('minima') from e
        return result

    @cached_property
    def domain(self, /) -> Expression:
        try:
            kwargs = {
                'symbol': self.parser.variables[0].eval(),
                'domain': Reals,
                **self.kwargs
            }
            return continuous_domain(self.parsed_equation.lhs, **kwargs) # type: ignore
        except (ValueError, IndexError) as e:
            raise CantGetProperty('domain') from e

    @cached_property
    def range(self, /) -> Expression:
        try:
            kwargs = {
                'symbol': self.parser.variables[0].eval(),
                'domain': Reals,
                **self.kwargs
            }
            return function_range(self.parsed_equation.lhs, **kwargs) # type: ignore
        except (ValueError, IndexError) as e:
            raise CantGetProperty('range') from e