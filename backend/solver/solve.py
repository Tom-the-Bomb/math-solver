from __future__ import annotations

from typing import TYPE_CHECKING, Optional, ClassVar, Final, Any
from functools import cache, cached_property
from contextlib import redirect_stdout
from io import StringIO, BytesIO
import warnings

import matplotlib
matplotlib.use('agg')
from matplotlib import pyplot as plt

import numpy as np
from sympy import (
    oo,
    Reals,
    pprint,
    Interval,
    Symbol,
    Derivative,
    latex as s_latex,
    diff, factor, expand, simplify,
    maximum, minimum,
    solve as s_solve,
    solveset as s_solveset,
    Eq, Ne, Ge, Le, Gt, Lt,
)
from sympy.calculus.util import function_range, continuous_domain
from sympy.core.relational import Relational
from sympy.logic.boolalg import BooleanAtom

from .parser import Parser, Constants, Functions
from .ast import Ast, CompoundInterval, DefinedFunction, BooleanResult, Equation, Expr
from .exceptions import *

if TYPE_CHECKING:
    from sympy import Set, Number
    from matplotlib.text import Text

class BooleanComp:
    def __init__(self, lhs: Expr, typ: Relational, rhs: Expr, /) -> None:
        self.lhs = lhs
        self.typ = typ
        self.rhs = rhs

    def __repr__(self, /) -> str:
        return f"<{self.__class__.__name__} '{self.to_latex()}'>"

    def to_latex(self, /) -> str:
        key = {
            Eq: '=',
            Ne: r'\ne',
            Gt: '>',
            Lt: '<',
            Ge: r'\ge',
            Le: r'\le',
        }.get(self.typ, self.typ.__name__) # type: ignore
        return f'{Solver.to_latex(self.lhs)}{key}{Solver.to_latex(self.rhs)}'

class Solver:
    GRAPH_AXES_COLOR: ClassVar[str] = '#413939'
    GRAPH_LINE_COLOR: ClassVar[str] = '#EFB8CA'
    GRAPH_GRID_COLOR: ClassVar[str] = '#634848'

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
                    parsed = Parser(constants=constants, is_parsing_function=True).parse(f)
                    if not isinstance(parsed, DefinedFunction):
                        raise NotAFunction(f)
                    parsed_functions.update(parsed.eval())
            self.parser = parser or Parser(
                constants=constants,
                functions=parsed_functions,
            )
            self.parsed_equation

            self._domain: Optional[Interval]
            if domain:
                if set_ := CompoundInterval.NUMBER_SETS.get(domain.strip().lower()):
                    self._domain = set_
                else:
                    try:
                        parsed = Parser().parse(domain).eval()
                        if not isinstance(parsed, Interval):
                            raise InvalidDomainParsed(domain)
                    except (SyntaxError, ValueError) as e:
                        raise InvalidDomainParsed(domain) from e
                    self._domain = parsed
            else:
                self._domain = None
        self.solve_for = solve_for

        self._kwargs = {}
        if self._domain is not None:
            self._kwargs['domain'] = self._domain
        if self.solve_for is not None:
            self._kwargs['symbol'] = Symbol(self.solve_for)

    def graph(self, /) -> BytesIO:
        fig = plt.figure(1, figsize=(10, 10))
        ax = fig.add_subplot(1, 1, 1)

        try:
            variable = self._kwargs.get(
                'symbol',
                self.parser.variables[0].eval()
            )
        except IndexError:
            variable = None
        def f(x):
            if variable is not None:
                val = self.lhs_equation.subs(variable, x)
            else:
                val = self.lhs_equation
            try:
                float(val)
                return val
            except TypeError:
                return
        fx = np.vectorize(f)

        if self._domain:
            x1, x2 = float(self._domain.start), float(self._domain.end)
        else:
            x1, x2 = -20, 20
        x = np.linspace(x1, x2, 500)
        ax.spines['bottom'].set_position('zero')
        ax.spines['bottom'].set_color(self.GRAPH_AXES_COLOR)

        ax.spines['left'].set_position('zero')
        ax.spines['left'].set_color(self.GRAPH_AXES_COLOR)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')

        ax.grid(which='both', color=self.GRAPH_GRID_COLOR, linewidth=1, linestyle='-', alpha=0.2)
        for tick in ax.get_xticklabels() + ax.get_yticklabels():
            tick: Text
            tick.set_fontsize(8)

        ax.plot(x, fx(x), color=self.GRAPH_LINE_COLOR)

        arrow_fmt = dict(markersize=4, color=self.GRAPH_AXES_COLOR, clip_on=False)
        ax.plot((1), (0), marker='>', transform=ax.get_yaxis_transform(), **arrow_fmt)
        ax.plot((0), (1), marker='^', transform=ax.get_xaxis_transform(), **arrow_fmt)

        buffer = BytesIO()
        fig.savefig(buffer,
            dpi=300,
            bbox_inches='tight',
            pad_inches=0,
            transparent=True,
        )
        plt.close()
        buffer.seek(0)
        return buffer

    @cached_property
    def derivative(self, /) -> Derivative:
        """Returns the first derivative of the function: d/dx"""
        symbols = [self.solve_for] if self.solve_for else [v.eval() for v in self.parser.variables]
        return diff(self.lhs_equation, *set(symbols))

    @cached_property
    def lhs_equation(self, /) -> Expr:
        """Isolates all parts of the equation to the LHS <- (LHS - RHS = 0)"""
        if isinstance(a := self._final_ast, BooleanResult):
            return a.conditional.left.eval() - a.conditional.right.eval()
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
            return s_solveset(self.parsed_equation, **self._kwargs)
        except Exception as e:
            try:
                return s_solve(self.parsed_equation, **self._kwargs)
            except Exception as e2:
                raise e from e2

    @staticmethod
    def to_latex(expr: Any) -> str:
        """Converts parsed expression to latex"""
        if hasattr(expr, 'to_latex'):
            return expr.to_latex()
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
        return factor(self.lhs_equation)

    @cached_property
    def expanded(self, /) -> Expr:
        """(x + 1)(x + 2) -> x^2 + 3x + 2"""
        return expand(self.lhs_equation)

    @cache
    def simplify(self, /, *, evaluate_bool: bool = False) -> Expr | BooleanComp:
        """2x + 1 + 3x + 2 -> 5x + 3"""
        simplified = simplify(self.parsed_equation)
        if not evaluate_bool and isinstance(a := self._final_ast, BooleanResult):
            return BooleanComp(a.lhs, a.sympy_conditional, a.rhs)
        if not evaluate_bool and isinstance(simplified, BooleanAtom):
            lhs = simplify(self.parsed_equation.lhs)
            rhs = simplify(self.parsed_equation.rhs)
            return BooleanComp(lhs, type(self.parsed_equation), rhs)
        return simplified

    @cached_property
    def max_min(self, /) -> dict[str, Number]:
        """Returns a dictionary containing the maxima and/or the minima, if exists"""
        result = {}
        try:
            kwargs = {
                'symbol': self.parser.variables[0].eval(),
                **self._kwargs
            }

            if abs(maxima := maximum(self.lhs_equation, **kwargs)) != oo: # type: ignore
                result['max'] = maxima
            if abs(minima := minimum(self.lhs_equation, **kwargs)) != oo: # type: ignore
                result['min'] = minima
        except Exception as e:
            return {'max': self.lhs_equation, 'min': self.lhs_equation}
        return result

    @cached_property
    def domain(self, /) -> Expr:
        """Returns the domain of the function"""
        try:
            kwargs = {
                'symbol': self.parser.variables[0].eval(),
                'domain': Reals,
                **self._kwargs
            }
            return continuous_domain(self.lhs_equation, **kwargs) # type: ignore
        except Exception as e:
            raise CantGetProperty('domain', e) from e

    @cached_property
    def range(self, /) -> Expr:
        """Returns the range of the function"""
        try:
            kwargs = {
                'symbol': self.parser.variables[0].eval(),
                'domain': Reals,
                **self._kwargs
            }
            return function_range(self.lhs_equation, **kwargs) # type: ignore
        except Exception as e:
            raise CantGetProperty('range', e) from e