from __future__ import annotations

from typing import Any, Callable, TypeAlias, Optional, TYPE_CHECKING
from abc import ABC, abstractmethod
from decimal import Decimal
from click import argument

from sympy import (
    Symbol,
    Eq as S_Eq,
    Lt as S_Lt,
    Le as S_Le,
    Gt as S_Gt,
    Ge as S_Ge,
)

from sympy.functions import factorial
from rply.token import BaseBox

if TYPE_CHECKING:
    from sympy.core.operations import AssocOp
    from sympy.core.relational import Relational
    from sympy.core.numbers import NumberSymbol

    Expr: TypeAlias = AssocOp | Decimal | int
    Equation: TypeAlias = Relational | bool

__all__ = (
    'Ast',
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
    'Lt',
    'Le',
    'Gt',
    'Ge',
)

class Ast(ABC, BaseBox):
    def __init__(self, value: str, /) -> None:
        self.value = value

    @abstractmethod
    def eval(self, /) -> Any:
        raise NotImplementedError

class Function(Ast):
    def __init__(self, func: Callable[..., Any], /, *arguments: Ast) -> None:
        self.func = func
        self.arguments = arguments

    def eval(self, /) -> Callable[..., Any]:
        return self.func(*[a.eval() for a in self.arguments])

class Constant(Ast):
    def __init__(self, value: NumberSymbol | Decimal | int, /) -> None:
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
        print('Bin |', self.left.eval(), self.__class__.__name__, self.right.eval())

    def eval(self, /) -> Number:
        raise NotImplementedError

class UnaryOp(Ast):
    def __init__(self, right: Ast, /):
        self.right = right
        print('Un |', self.__class__.__name__, self.right.eval())

    def eval(self, /) -> Number:
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
    def __init__(self, x: Any, /) -> None:
        self.x = x

    def eval(self, /) -> factorial:
        return factorial(self.x)

class Conditional(BinaryOp, ABC):
    @abstractmethod
    def eval(self, /) -> Equation:
        raise NotImplementedError

class Eq(Conditional):
    def eval(self, /) -> Equation:
        return S_Eq(self.left.eval(), self.right.eval())

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