from __future__ import annotations
from decimal import Decimal

from typing import Optional, Callable, Any, TYPE_CHECKING
import inspect

from rply import Token, ParserGenerator
from sympy import (
    E, I, pi, GoldenRatio, oo,
    functions as func_mod
)

from .lexer import LexerGenerator
from .ast import *

if TYPE_CHECKING:
    from sympy import NumberSymbol

class Parser:
    lg = LexerGenerator()
    pg = ParserGenerator(
        [
            token.name for token in lg.rules
        ],
        precedence=[
            ('right', ['UNOP']),
            ('left', ['ADD', 'SUB']),
            ('left', ['MUL', 'DIV', 'MOD']),
            ('right', ['POW']),
            ('left', ['FAC']),
        ]
    )

    def __init__(
        self, /,
        *,
        functions: Optional[dict[str, Callable[[Any], Any]]] = None,
        constants: Optional[dict[str, Decimal | NumberSymbol | int]] = None,
    ) -> None:
        self.functions = functions or dict(inspect.getmembers(func_mod))
        self.constants = constants or {
            'e': E,
            'i': I,
            'pi': pi,
            'tau': 2 * pi,
            'phi': GoldenRatio,
            'inf': oo,
        }

    def parse(self, equation: str) -> Conditional:
        lexer = self.lg.build()
        parser = self.pg.build()

        return parser.parse(lexer.lex(equation), state=self) # type: ignore

    @staticmethod
    @pg.production('equation : expr')
    @pg.production('equation : expr EQ expr')
    @pg.production('equation : expr LT expr')
    @pg.production('equation : expr LE expr')
    @pg.production('equation : expr GT expr')
    @pg.production('equation : expr GE expr')
    def equation(_, p: list[Token], /) -> BinaryOp:
        if len(p) == 1:
            return Eq(p[0], Number('0')) # type: ignore

        return {
            'EQ': Eq,
            'LT': Lt,
            'LE': Le,
            'GT': Gt,
            'GE': Ge,
        }[p[1].gettokentype()](p[0], p[2])

    @staticmethod
    @pg.production('expr : NUMBER')
    def number(_, p: list[Token], /) -> Number:
        return Number(p[0].getstr())

    @staticmethod
    @pg.production('expr : LPAREN expr RPAREN')
    @pg.production('expr : LBRACK expr RBRACK')
    @pg.production('expr : LBRACE expr RBRACE')
    def paren(_, p: list[Token], /) -> Ast:
        return p[1] # type: ignore

    @staticmethod
    @pg.production('expr : expr FAC')
    def factorial(_, p: list[Token], /) -> Fac:
        return Fac(p[0].getstr())

    @staticmethod
    @pg.production('expr : expr ADD expr')
    @pg.production('expr : expr SUB expr')
    @pg.production('expr : expr MUL expr')
    @pg.production('expr : expr DIV expr')
    @pg.production('expr : expr MOD expr')
    @pg.production('expr : expr POW expr')
    def binop(_, p: list[Token], /) -> BinaryOp:
        return {
            'ADD': Add,
            'SUB': Sub,
            'MUL': Mul,
            'DIV': Div,
            'MOD': Mod,
            'POW': Pow,
        }[p[1].gettokentype()](p[0], p[2])

    @staticmethod
    @pg.production('expr : IDENT')
    def variable(state: Parser, p: list[Token], /) -> Constant | Variable | Mul:
        ident = p[0].getstr()

        if x := state.constants.get(ident):
            return Constant(ident)
        if len(ident) == 1:
            return Variable(ident)

        variables = map(Variable, ident)
        expr = Mul(next(variables), next(variables))
        for x in variables:
            expr = Mul(expr, x)
        return expr

    @staticmethod
    @pg.production('expr : IDENT LPAREN expr RPAREN')
    def fx(state: Parser, p: list[Token], /) -> Function | Mul:
        if f := state.functions.get(p[0].getstr()):
            return Function(f, p[2]) # type: ignore

        return Mul(Variable(p[0].getstr()), p[2]) # type: ignore

    @staticmethod
    @pg.production("expr : ADD expr", precedence='UNOP')
    @pg.production("expr : SUB expr", precedence='UNOP')
    def unop(_, p: list[Token], /) -> UnaryOp:
        return {
            'ADD': Pos,
            'SUB': Neg,
        }[p[0].gettokentype()](p[1])

    @staticmethod
    @pg.production('expr : expr expr', precedence='MUL')
    def implcit_mul(_, p: list[Ast], /) -> Any:
        return Mul(p[0], p[1])