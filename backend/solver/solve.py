from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Any
from functools import cache, cached_property
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
    Eq, Ne, Ge, Le, Gt, Lt,
)
from sympy.calculus.util import function_range, continuous_domain
from sympy.logic.boolalg import BooleanAtom

from .parser import Parser, Constants, Functions
from .ast import Ast, DefinedFunction, BooleanResult, Equation, Expr
from .exceptions import *

if TYPE_CHECKING:
    from sympy import Set
    from sympy import Number

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
        self._final_ast: Optional[Ast] = None

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

            self._domain: Interval = Parser().parse(domain).eval() if domain else None
        self.solve_for = solve_for

        self.kwargs = {}
        if self._domain is not None:
            self.kwargs['domain'] = self._domain
        if self.solve_for:
            self.kwargs['symbol'] = self.solve_for

    @cached_property
    def lhs_equation(self, /) -> Expr:
        """Isolates all parts of the equation to the LHS <- (LHS - RHS = 0)"""
        return self.parsed_equation.lhs - self.parsed_equation.rhs

    @cached_property
    def parsed_equation(self, /) -> Equation | Interval | Functions:
        """Returns the parsed and evaluated equation from the Lexer -> Parser -> Ast"""
        self._final_ast = self.parser.parse(self.raw_equation)
        return self._final_ast.eval()

    @cached_property
    def solution(self, /) -> Set | list[Any]:
        """Returns the raw solution still represented by SymPy objectss"""
        try:
            return s_solveset(self.parsed_equation, **self.kwargs)
        except Exception as e:
            try:
                return s_solve(self.parsed_equation, **self.kwargs)
            except Exception as e2:
                raise e from e2

    def to_latex(self, expr: Expr | Equation | str) -> str:
        """Converts parsed expression to latex"""
        if isinstance(expr, str):
            return expr
        return s_latex(expr)

    @cache
    def parsed_solution(self, /, *, evaluate_bool: bool = False) -> str:
        """prettified and formatted solution"""
        if not evaluate_bool and isinstance(a := self._final_ast, BooleanResult):
            return a.to_latex()
        buf = StringIO()
        with redirect_stdout(buf):
            pprint(self.solution)
        return buf.getvalue()

    @cache
    def ascii_parsed_solution(self, /, *, evaluate_bool: bool = False) -> str:
        """(non unicode) prettified and formatted solution"""
        if not evaluate_bool and isinstance(a := self._final_ast, BooleanResult):
            return a.to_latex()
        buf = StringIO()
        with redirect_stdout(buf):
            pprint(self.solution, use_unicode=False)
        return buf.getvalue()

    @cached_property
    def factored(self, /) -> Expr:
        """x^2 - 4 -> (x + 2)(x - 2)"""
        return factor(self.parsed_equation)

    @cached_property
    def expanded(self, /) -> Expr:
        """(x + 1)(x + 2) -> x^2 + 3x + 2"""
        return expand(self.parsed_equation)

    @cache
    def simplify(self, /, *, evaluate_bool: bool = False) -> Expr | str:
        """2x + 1 + 3x + 2 -> 5x + 3"""
        simplified = simplify(self.parsed_equation)
        if not evaluate_bool and isinstance(a := self._final_ast, BooleanResult):
            return a.to_latex()
        if not evaluate_bool and isinstance(simplified, BooleanAtom):
            lhs = simplify(self.parsed_equation.lhs)
            rhs = simplify(self.parsed_equation.rhs)
            key = {
                Eq: '=',
                Ne: r'\ne',
                Gt: '>',
                Lt: '<',
                Ge: r'\ge',
                Le: r'\le',
            }[type(self.parsed_equation)]
            return f'{lhs}{key}{rhs}'
        return simplified

    @cached_property
    def max_min(self, /) -> dict[str, Number]:
        """Returns a dictionary containing the maxima and/or the minima, if exists"""
        result = {}
        kwargs = {
            'symbol': self.parser.variables[0].eval(),
            **self.kwargs
        }

        try:
            if abs(maxima := maximum(self.lhs_equation, **kwargs)) != oo: # type: ignore
                result['max'] = maxima
        except (ValueError, IndexError) as e:
            raise CantGetProperty('maxima') from e
        try:
            if abs(minima := minimum(self.lhs_equation, **kwargs)) != oo: # type: ignore
                result['min'] = minima
        except (ValueError, IndexError) as e:
            raise CantGetProperty('minima') from e
        return result

    @cached_property
    def domain(self, /) -> Expr:
        """Returns the domain of the function"""
        try:
            kwargs = {
                'symbol': self.parser.variables[0].eval(),
                'domain': Reals,
                **self.kwargs
            }
            return continuous_domain(self.lhs_equation, **kwargs) # type: ignore
        except (ValueError, IndexError) as e:
            raise CantGetProperty('domain') from e

    @cached_property
    def range(self, /) -> Expr:
        """Returns the range of the function"""
        try:
            kwargs = {
                'symbol': self.parser.variables[0].eval(),
                'domain': Reals,
                **self.kwargs
            }
            return function_range(self.lhs_equation, **kwargs) # type: ignore
        except (ValueError, IndexError) as e:
            raise CantGetProperty('range') from e