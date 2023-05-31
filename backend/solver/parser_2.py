from __future__ import annotations

from typing import ClassVar, NoReturn, Optional, Callable, Any, TYPE_CHECKING
from decimal import Decimal
import inspect

from rply import Token, ParserGenerator
from rply.lexer import SourcePosition, LexingError
from sympy import (
    E, I, pi, GoldenRatio, oo,
    functions as func_mod
)

from .lexer import LexerGenerator
from .ast import *

if TYPE_CHECKING:
    from rply.lexer import Lexer
    from rply.parser import LRParser

    from sympy import NumberSymbol

__all__ = ('Parser',)

def _to_camel_case(string: str) -> str:
    terms = iter(string.split('_'))
    return next(terms) + ''.join(t.title() for t in terms)

class Parser:
    lg: ClassVar[LexerGenerator] = LexerGenerator()
    pg: ClassVar[ParserGenerator] = ParserGenerator(
        [
            token.name for token in lg.rules
        ],
        precedence=[
            ('right', ['UNOP']),
            ('left', ['ADD', 'SUB']),
            ('left', ['MUL', 'DIV', 'MOD']),
            ('left', ['IMPL_MUL']),
            ('right', ['POW']),
            ('left', ['FAC']),
        ]
    )

    def __init__(
        self, /,
        *,
        functions: Optional[dict[str, Callable[..., Any]]] = None,
        constants: Optional[dict[str, Decimal | NumberSymbol | int]] = None,
    ) -> None:
        self.functions = {
            **{_to_camel_case(k): v for k, v in inspect.getmembers(func_mod)},
            **(functions or {})
        }
        self.constants = {**{
            'e': E,
            'i': I,
            'pi': pi,
            'tau': 2 * pi,
            'phi': GoldenRatio,
            'inf': oo,
        }, **(constants or {})}

        self.variables: list[Variable] = []

        self._lexer: Lexer = self.lg.build()
        self._parser: LRParser = self.pg.build()

    def parse(self, equation: str) -> Conditional:
        try:
            return self._parser.parse(
                self._lexer.lex(equation),
                state=self
            ) # type: ignore
        except LexingError as e:
            pos: SourcePosition = e.getsourcepos()
            raise SyntaxError(f"Invalid token {e.message or ''} @ {pos.lineno}:{pos.colno}")

    @staticmethod
    @pg.production('equation : expr')
    @pg.production('equation : expr EQ expr')
    @pg.production('equation : expr FAC EQ expr')
    @pg.production('equation : expr LT expr')
    @pg.production('equation : expr LT EQ expr')
    @pg.production('equation : expr GT expr')
    @pg.production('equation : expr GT EQ expr')
    def equation(_, p: list[Token], /) -> BinaryOp:
        if len(p) == 1 and isinstance(p[0], Ast):
            return Eq(p[0], Number('0'))

        return {
            ('EQ', None): Eq,
            ('FAC', 'EQ'): Ne,
            ('LT', None): Lt,
            ('LT', 'EQ'): Le,
            ('GT', None): Gt,
            ('GT', 'EQ'): Ge,
        }[(p[1].gettokentype(), getattr(p[2], 'gettokentype', lambda: None)())](p[0], p[-1])

    @pg.production('expr : group')
    def group(_, p: list[Ast], /) -> Ast:
        return p[0]

    @staticmethod
    @pg.production('group : group group', precedence='IMPL_MUL')
    def implicit_mul(_, p: list[Ast], /) -> Mul:
        return Mul(p[0], p[1])

    @pg.production('group : NUMBER')
    def number(_, p: list[Token], /) -> Number:
        return Number(p[0].getstr())

    @staticmethod
    @pg.production('group : LBRACK expr RBRACK')
    @pg.production('group : LBRACE expr RBRACE')
    def paren(_, p: list[Ast], /) -> Ast:
        return p[1] if len(p) == 3 else p[0]

    @staticmethod
    @pg.production('group : group FAC')
    def factorial(_, p: list[Token], /) -> Fac:
        return Fac(p[0].getstr())

    @staticmethod
    @pg.production('expr : expr ADD expr', precedence='ADD')
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
    @pg.production('group : IDENT LBRACK expr RBRACK')
    @pg.production('group : IDENT SUBSCRIPT expr LBRACK expr RBRACK')
    def fx(state: Parser, p: list[Ast], /) -> Function | Mul:
        assert isinstance(p[0], Token)

        ident = p[0].getstr()
        if f := state.functions.get(ident):
            arguments = (p[2],)
            if len(p) == 6:
                arguments += (p[-2],)
            return Function(f, *arguments)

        return Mul(Variable(ident), p[-2])

    @staticmethod
    @pg.production('group : IDENT')
    def variable(state: Parser, p: list[Token], /) -> Constant | Variable | Mul | Function:
        ident = p[0].getstr()
        if len(p) == 3:
            ident += f'_{p[-1].getstr()}'

        if x := state.constants.get(ident):
            return Constant(x)

        if len(ident) == 1 or len(p) == 3:
            var = Variable(ident)
            state.variables.append(var)
            return var

        variables = map(Variable, ident)
        expr = Mul(next(variables), next(variables))
        for x in variables:
            if con := state.constants.get(ident):
                x = Constant(con)
            else:
                state.variables.append(x)
            expr = Mul(expr, x)
        return expr

    @staticmethod
    @pg.production("expr : ADD group", precedence='UNOP')
    @pg.production("expr : SUB group", precedence='UNOP')
    def unop(_, p: list[Token], /) -> UnaryOp:
        return {
            'ADD': Pos,
            'SUB': Neg,
        }[p[0].gettokentype()](p[1])

    @staticmethod
    @pg.error
    def error_handler(_, token: Token) -> NoReturn:
        pos: Optional[SourcePosition] = token.getsourcepos()
        raise ValueError(
            f"Encountered a {token.gettokentype()}: '{token.getstr()}' "
            f"@ {getattr(pos, 'lineno', 'x')}:{getattr(pos, 'colno', 'x')} where it was not expected"
        )