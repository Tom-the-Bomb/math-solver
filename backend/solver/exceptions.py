from __future__ import annotations
from typing import TYPE_CHECKING

__all__ = (
    'SolverException',
    'SolverOverflow',
    'NumberLiteralOverflow',
    'ExponentOverflow',
    'FactorialOverflow',
    'MathTimeout',
    'InvalidDomainParsed',
    'InvalidFunctionArgument',
    'InvalidFunctionCall',
    'NotAFunction',
    'CantGetProperty',
)

if TYPE_CHECKING:
    from decimal import Decimal
    from .parser import Expr

class SolverException(Exception):
    ...

class SolverOverflow(SolverException, OverflowError):
    ...

class NumberLiteralOverflow(SolverOverflow):
    def __init__(self, value: int | Decimal, max_value: float) -> None:
        super().__init__(f'Number with a value of {value} exceeds the maximum allowed number literal of: {max_value}.')

class ExponentOverflow(SolverOverflow):
    def __init__(self, value: Expr, max_value: float) -> None:
        super().__init__(f'An exponent of {value} exceeds the maximum allowed exponent of: {max_value}.')

class FactorialOverflow(SolverOverflow):
    def __init__(self, value: Expr, max_value: float) -> None:
        super().__init__(f'An expression with a value of {value} exceeds the maximum allowed factorial of: {max_value}.')

class MathTimeout(SolverException):
    def __init__(self, timeout: float, /) -> None:
        super().__init__(self, f'Processing exceeded the set time limit of {timeout}s')

class InvalidDomainParsed(SolverException):
    def __init__(self, got: str, /) -> None:
        super().__init__(f'"{got}" is an invalid domain expression')

class InvalidFunctionArgument(SolverException):
    def __init__(self, /) -> None:
        super().__init__('Invalid function argument recieved')

class InvalidFunctionCall(SolverException):
    def __init__(self, ident: str, /) -> None:
        super().__init__(f'Undefined function: {ident}')

class NotAFunction(SolverException):
    def __init__(self, provided: str, /) -> None:
        super().__init__(f'Invalid function syntax: {provided}\nCorrect Ex: f(x) = x^2')

class CantGetProperty(SolverException):
    def __init__(self, property: str, error: Exception, /) -> None:
        super().__init__(f'Unable to retrieve <{property}> from provided function / expression:\n{error}')