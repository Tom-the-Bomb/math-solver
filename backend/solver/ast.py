from __future__ import annotations

from typing import Any, Callable, TypeAlias, TYPE_CHECKING
from abc import ABC, abstractmethod
from decimal import Decimal

from sympy import Symbol
from sympy.functions import factorial
from rply.token import BaseBox

if TYPE_CHECKING:
    from sympy.core.operations import AssocOp
    from sympy import (
        Add as S_Add,
        Mul as S_Mul,
        Pow as S_Pow,
    )

    Expr: TypeAlias = AssocOp | Decimal

__all__ = (
    'Ast',
    'Function',
    'Variable',
    'Number',
    'Pos',
    'Neg',
    'Add',
    'Sub',
    'Mul',
    'Div',
    'Mod',
    'Pow',
    'Fac',
)

class Ast(ABC, BaseBox):
    def __init__(self, value: str, /) -> None:
        self.value = value

    @abstractmethod
    def eval(self, /) -> Any:
        raise NotImplementedError

class Function(Ast):
    def __init__(self, func: Callable[[Any], Any], argument: Ast, /) -> None:
        self.func = func
        self.argument = argument

    def eval(self, /) -> Symbol:
        return self.func(self.argument.eval())

class Variable(Ast):
    def eval(self, /) -> Symbol:
        return Symbol(self.value)

class Number(Ast):
    def eval(self, /) -> Decimal:
        return Decimal(self.value)

class _BinaryOp(Ast):
    def __init__(self, left: Ast, right: Ast, /):
        self.left = left
        self.right = right

    def eval(self, /) -> Number:
        raise NotImplementedError

class _UnaryOp(Ast):
    def __init__(self, right: Ast, /):
        self.right = right

    def eval(self, /) -> Number:
        raise NotImplementedError

class Pos(_UnaryOp):
    def eval(self, /) -> Expr:
        return +self.right.eval()

class Neg(_UnaryOp):
    def eval(self, /) -> Expr:
        return -self.right.eval()

class Add(_BinaryOp):
    def eval(self, /) -> Expr:
        return self.left.eval() + self.right.eval()

class Sub(_BinaryOp):
    def eval(self, /) -> Expr:
        return self.left.eval() - self.right.eval()

class Mul(_BinaryOp):
    def eval(self, /) -> Expr:
        return self.left.eval() * self.right.eval()

class Div(_BinaryOp):
    def eval(self, /) -> Expr:
        return self.left.eval() / self.right.eval()

class Mod(_BinaryOp):
    def eval(self, /) -> Expr:
        return self.left.eval() % self.right.eval()

class Pow(_BinaryOp):
    def eval(self, /) -> Expr:
        return self.left.eval() ** self.right.eval()

class Fac(Ast):
    def __init__(self, x: Any, /) -> None:
        self.x = x

    def eval(self, /) -> factorial:
        return factorial(self.x)