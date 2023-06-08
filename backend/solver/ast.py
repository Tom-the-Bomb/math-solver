from __future__ import annotations

from typing import Any, Callable, Optional, TypeAlias, TYPE_CHECKING
from abc import ABC, abstractmethod
from decimal import Decimal

from sympy import (
    Symbol,
    Interval as S_Interval,
    Eq as S_Eq,
    Ne as S_Ne,
    Lt as S_Lt,
    Le as S_Le,
    Gt as S_Gt,
    Ge as S_Ge,
)

from sympy.functions import factorial
from sympy.core.basic import Basic
from sympy.core.relational import Relational

from rply.token import BaseBox

from .exceptions import *

if TYPE_CHECKING:
    from sympy.core.numbers import NumberSymbol

    from .parser import Functions

__all__ = (
    'Ast',
    'DefinedFunction',
    'Interval',
    'Function',
    'Constant',
    'Variable',
    'Number',
    'BinaryOp',
    'UnaryOp',
    'Conditional',
    'Pos',
    'Neg',
    'Add',
    'Sub',
    'Mul',
    'Div',
    'Mod',
    'Pow',
    'Fac',
    'Eq',
    'Ne',
    'Lt',
    'Le',
    'Gt',
    'Ge',
    'BooleanResult',
    'Expr',
    'Equation',
)

Expr: TypeAlias = Basic | Decimal | int
Equation: TypeAlias = Relational | bool

class Ast(ABC, BaseBox):
    def __init__(self, value: str, /) -> None:
        self.value = value

    @abstractmethod
    def eval(self, /) -> Any:
        raise NotImplementedError

class Interval(Ast):
    def __init__(self, left: str, a: Ast, b: Ast, right: str) -> None:
        self.brackets = left + right
        self.a = a
        self.b = b

    def eval(self, /) -> S_Interval:
        return {
            '[]': S_Interval,
            '()': S_Interval.open,
            '(]': S_Interval.Lopen,
            '[)': S_Interval.Ropen,
        }[self.brackets](self.a.eval(), self.b.eval())

class DefinedFunction(Ast):
    def __init__(self, f_name: str, arguments: list[Ast], expression: Ast) -> None:
        self.f_name = f_name
        self.arguments = arguments
        self.expression = expression

    def eval(self, /) -> Functions:
        raw_function = self.expression.eval()

        if self.arguments and isinstance(raw_function, Basic):
            def f(*args) -> Expr:
                nonlocal raw_function
                for arg_name, arg_val in zip(self.arguments, args):
                    if name := getattr(arg_name, 'value', None):
                        if isinstance(arg_name, Constant):
                            name = arg_name.ident
                        raw_function = raw_function.subs(Symbol(name), arg_val)
                    else:
                        raise InvalidFunctionArgument()
                return raw_function
            function = f
        elif self.arguments:
            function = lambda *_: raw_function
        else:
            function = lambda: raw_function
        return {self.f_name: function}

class Function(Ast):
    def __init__(self, func: Callable[..., Any], /, *arguments: Ast) -> None:
        self.func = func
        self.arguments = arguments

    def eval(self, /) -> Callable[..., Any]:
        return self.func(*[a.eval() for a in self.arguments])

class Constant(Ast):
    def __init__(self, ident: str, value: NumberSymbol | Decimal | int, /) -> None:
        self.ident = ident
        self.value = value

    def eval(self, /) -> NumberSymbol | Decimal | int:
        return self.value

class Variable(Ast):
    def eval(self, /) -> Symbol:
        return Symbol(self.value)

class Number(Ast):
    def eval(self, /) -> Decimal | int:
        return int(self.value) if float(self.value).is_integer() else Decimal(self.value)

class BinaryOp(Ast):
    def __init__(self, left: Ast, right: Ast, /):
        self.left = left
        self.right = right

    def eval(self, /) -> Expr:
        raise NotImplementedError

class UnaryOp(Ast):
    def __init__(self, right: Ast, /):
        self.right = right

    def eval(self, /) -> Expr:
        raise NotImplementedError

class Pos(UnaryOp):
    def eval(self, /) -> Expr:
        return +self.right.eval()

class Neg(UnaryOp):
    def eval(self, /) -> Expr:
        return -self.right.eval()

class Add(BinaryOp):
    def eval(self, /) -> Expr:
        return self.left.eval() + self.right.eval()

class Sub(BinaryOp):
    def eval(self, /) -> Expr:
        return self.left.eval() - self.right.eval()

class Mul(BinaryOp):
    def eval(self, /) -> Expr:
        return self.left.eval() * self.right.eval()

class Div(BinaryOp):
    def eval(self, /) -> Expr:
        return self.left.eval() / self.right.eval()

class Mod(BinaryOp):
    def eval(self, /) -> Expr:
        return self.left.eval() % self.right.eval()

class Pow(BinaryOp):
    def eval(self, /) -> Expr:
        return self.left.eval() ** self.right.eval()

class Fac(Ast):
    def __init__(self, x: Ast, /) -> None:
        self.x = x

    def eval(self, /) -> factorial:
        return factorial(self.x.eval())

class Conditional(BinaryOp, ABC):
    @abstractmethod
    def eval(self, /) -> Equation:
        raise NotImplementedError

class Eq(Conditional):
    def eval(self, /) -> Equation:
        return S_Eq(self.left.eval(), self.right.eval())

class Ne(Conditional):
    def eval(self, /) -> Equation:
        return S_Ne(self.left.eval(), self.right.eval())

class Lt(Conditional):
    def eval(self, /) -> Equation:
        return S_Lt(self.left.eval(), self.right.eval())

class Le(Conditional):
    def eval(self, /) -> Equation:
        return S_Le(self.left.eval(), self.right.eval())

class Gt(Conditional):
    def eval(self, /) -> Equation:
        return S_Gt(self.left.eval(), self.right.eval())

class Ge(Conditional):
    def eval(self, /) -> Equation:
        return S_Ge(self.left.eval(), self.right.eval())

class BooleanResult(Ast):
    def __init__(self, conditional: Conditional) -> None:
        self.conditional = conditional

    def __repr__(self, /) -> str:
        return f"<{self.__class__.__name__} '{self.to_latex()}'>"

    def to_latex(self, /) -> str:
        name = self.conditional.__class__.__name__
        key = {
            'Eq': '=',
            'Ne': r'\ne',
            'Gt': '>',
            'Lt': '<',
            'Ge': r'\ge',
            'Le': r'\le',
        }.get(name, name)
        return f'{self.lhs}{key}{self.rhs}'

    @property
    def sympy_conditional(self, /) -> Relational:
        return {
            'Eq': S_Eq,
            'Ne': S_Ne,
            'Ge': S_Ge,
            'Le': S_Le,
            'Gt': S_Gt,
            'Lt': S_Lt,
        }.get(self.conditional.__class__.__name__, self.conditional)

    @property
    def lhs(self, /) -> Expr:
        return self.conditional.left.eval()

    @property
    def rhs(self, /) -> Expr:
        return self.conditional.right.eval()

    def eval(self, /) -> Equation:
        return self.conditional.eval()