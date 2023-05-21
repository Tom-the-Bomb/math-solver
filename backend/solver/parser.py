from __future__ import annotations

from typing import Optional, Callable, Any
import inspect

from rply import Token, ParserGenerator
from sympy import functions as func_mod

from .lexer import LexerGenerator
from .ast import *

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
        functions: Optional[dict[str, Callable[[Any], Any]]] = None
    ) -> None:
        self.functions = functions or dict(inspect.getmembers(func_mod))

    def parse(self, equation: str) -> Ast:
        lexer = self.lg.build()
        parser = self.pg.build()

        return parser.parse(lexer.lex(equation), state=self) # type: ignore

    @staticmethod
    @pg.production('expr : NUMBER')
    def number(_, p: list[Token], /) -> Number:
        return Number(p[0].getstr())

    @staticmethod
    @pg.production('expr : LPAREN expr RPAREN')
    @pg.production('expr : LBRACK expr RBRACK')
    @pg.production('expr : LBRACE expr RBRACE')
    def paren(_, p: list[Token], /) -> Any:
        return p[1]

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
    def binop(_, p: list[Token], /) -> ...:
        return {
            'ADD': Add,
            'SUB': Sub,
            'MUL': Mul,
            'DIV': Div,
            'MOD': Mod,
            'POW': Pow,
        }[p[1].gettokentype()](p[0], p[2])

    @staticmethod
    @pg.production('expr : NAME')
    def variable(_, p: list[Token], /) -> Any:
        return Variable(p[0].getstr())

    @staticmethod
    @pg.production('expr : NAME LPAREN expr RPAREN')
    def fx(state: Parser, p: list[Token], /) -> Any:
        if f := state.functions.get(p[0].getstr()):
            return Function(f, p[2]) # type: ignore

        return Mul(Variable(p[0].getstr()), p[2]) # type: ignore

    @staticmethod
    @pg.production("expr : ADD expr", precedence='UNOP')
    @pg.production("expr : SUB expr", precedence='UNOP')
    def unop(_, p: list[Token], /) -> Any:
        return {
            'ADD': Pos,
            'SUB': Neg,
        }[p[0].gettokentype()](p[1])