from __future__ import annotations

from typing import (
    TYPE_CHECKING, Any,
    TypeAlias, ClassVar, NoReturn, Optional, Callable, Iterable,
)
from decimal import Decimal
import inspect

from rply import Token, ParserGenerator
from rply.lexer import SourcePosition, LexingError
from sympy import (
    E, I, pi, GoldenRatio, oo,
    functions as func_mod,
    NumberSymbol,
)

from .lexer import LexerGenerator
from .ast import *

if TYPE_CHECKING:
    from rply.lexer import Lexer
    from rply.parser import LRParser

__all__ = (
    'Parser',
    'Functions',
    'Constants',
)

Functions: TypeAlias = dict[str, Callable[..., Any]]
Constants: TypeAlias = dict[str, Decimal | NumberSymbol | int]

def _to_camel_case(string: str) -> str:
    """Converts identifier from snake_case to camelCase

    * Required for function names to not conflict with subscripts on function names
    """
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
        functions: Optional[Functions] = None,
        constants: Optional[Constants] = None,
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

    def parse(self, equation: str) -> Conditional | DefinedFunction | Interval:
        try:
            return self._parser.parse(
                self._lexer.lex(equation),
                state=self
            ) # type: ignore
        except LexingError as e:
            pos: SourcePosition = e.getsourcepos()
            raise SyntaxError(f"Invalid token {e.message or ''} @ {pos.lineno}:{pos.colno}")

    @staticmethod
    @pg.production('equation : func EQ expr')
    def defined_function(_, p: list[Ast]) -> DefinedFunction:
        assert isinstance(p[0], list)
        f_name = p[0][0].getstr()
        argument = p[0][-2].value

        assert isinstance(p[-1], BinaryOp)
        return DefinedFunction(f_name, argument, p[-1])

    @staticmethod
    @pg.production('equation : LBRACK expr COMMA expr RBRACK')
    @pg.production('equation : LBRACK expr COMMA expr RPAREN')

    @pg.production('equation : LPAREN expr COMMA expr RBRACK')
    @pg.production('equation : LPAREN expr COMMA expr RPAREN')
    def domain_interval(_, p: list[Token]) -> Interval:
        assert isinstance(p[1], Ast)
        assert isinstance(p[-2], Ast)

        return Interval(p[0].getstr(), p[1], p[-2], p[-1].getstr())

    @staticmethod
    @pg.production('equation : expr')
    @pg.production('equation : expr EQ expr')
    @pg.production('equation : expr NE expr')
    @pg.production('equation : expr LT expr')
    @pg.production('equation : expr LT EQ expr')
    @pg.production('equation : expr GT expr')
    @pg.production('equation : expr GT EQ expr')
    def equation(_, p: list[Token], /) -> BinaryOp:
        if len(p) == 1 and isinstance(p[0], Ast):
            return Eq(p[0], Number('0'))

        return {
            ('EQ', None): Eq,
            ('NE', None): Ne,
            ('LT', None): Lt,
            ('LT', 'EQ'): Le,
            ('GT', None): Gt,
            ('GT', 'EQ'): Ge,
        }[(p[1].gettokentype(), getattr(p[2], 'gettokentype', lambda: None)())](p[0], p[-1])

    @staticmethod
    @pg.production('expr : group')
    def group(_, p: list[Ast], /) -> Ast:
        return p[0]

    @staticmethod
    @pg.production('group : group group', precedence='IMPL_MUL')
    def implicit_mul(_, p: list[Ast], /) -> Mul:
        return Mul(p[0], p[1])

    @staticmethod
    @pg.production('group : NUMBER')
    def number(_, p: list[Token], /) -> Number:
        return Number(p[0].getstr())

    @staticmethod
    @pg.production('group : LPAREN expr RPAREN')
    @pg.production('group : LBRACK expr RBRACK')
    @pg.production('group : LBRACE expr RBRACE')
    def paren(_, p: list[Ast], /) -> Ast:
        return p[1] if len(p) == 3 else p[0]

    @staticmethod
    @pg.production('group : group FAC')
    def factorial(_, p: list[Ast], /) -> Fac:
        return Fac(p[0])

    @staticmethod
    @pg.production('expr : expr ADD expr')
    @pg.production('expr : expr SUB expr')
    @pg.production('expr : expr MUL expr')
    @pg.production('expr : expr DIV expr')
    @pg.production('expr : expr MOD expr')

    @pg.production('group : group POW group')
    def binop(_, p: list[Ast], /) -> BinaryOp:
        assert isinstance(p[1], Token)
        return {
            'ADD': Add,
            'SUB': Sub,
            'MUL': Mul,
            'DIV': Div,
            'MOD': Mod,
            'POW': Pow,
        }[p[1].gettokentype()](p[0], p[2])

    @staticmethod
    @pg.production('func : IDENT LPAREN expr RPAREN')

    @pg.production('func : IDENT SUBSCRIPT NUMBER LPAREN expr RPAREN')
    @pg.production('func : IDENT SUBSCRIPT IDENT LPAREN expr RPAREN')

    @pg.production('func : IDENT SUBSCRIPT LPAREN expr RPAREN LPAREN expr RPAREN')
    def func(_, p: list[Ast]) -> list[Ast]:
        return p

    @staticmethod
    @pg.production('group : func')
    def fx(state: Parser, _p: list[list[Ast]], /) -> Function | Mul:
        p = _p[0]

        assert isinstance(p[0], Token)
        ident = p[0].getstr()

        subscript = None
        if len(p) == 8:
            subscript = p[3]
        elif len(p) == 6 and isinstance(tok := p[2], Token):
            subscript = {
                'NUMBER': Parser.number,
                'IDENT': Parser.variable,
            }[tok.gettokentype()](state, [tok])

        if f := state.functions.get(ident):
            arguments = (p[-2],)
            if len(p) in (6, 8) and subscript:
                arguments = (subscript,) + arguments
            return Function(f, *arguments)

        if len(p) in (6, 8) and subscript:
            ident += f'_{subscript.eval()}'
        return Mul(
            Parser.multi_var(
                state,
                [Parser.variable(state, [p[0]])],
            ),
            p[-2],
        )

    @staticmethod
    @pg.production('var : IDENT')
    @pg.production('var : IDENT SUBSCRIPT NUMBER')
    def variable(state: Parser, p: list[Token], /) -> Constant | Variable | Iterable[Variable]:
        ident = p[0].getstr()
        if len(p) == 3:
            ident += f'_{p[-1].getstr()}'

        if x := state.constants.get(ident):
            return Constant(x)

        raw = p[0].getstr()
        if len(ident) == 1 or len(raw) == 1:
            var = Variable(ident)
            state.variables.append(var)
            return var
        
        if len(p) == 3:
            return map(Variable, [*raw[:-1], raw[-1] + f'_{p[-1].getstr()}'])
        else:
            return map(Variable, ident)
    
    @pg.production('group : var POW group')
    @pg.production('group : var FAC')
    @pg.production('group : var')
    def multi_var(state: Parser, p: list[Ast | Iterable[Variable]]) -> Number | Constant | Variable | Mul | Fac | Pow:
        def do_op(var: Constant | Variable) -> Constant | Variable | Fac | Pow:
            match len(p):
                case 2:
                    return Fac(var)
                case 3:
                    assert isinstance(p[2], Ast)
                    return Pow(var, p[2])
                case _:
                    return var

        variables = p[0]
        if isinstance(variables, map):
            var_amt = len(variables := tuple(variables))
    
            expr = Number('1')
            for i, x in enumerate(variables):
                x: Variable
                if con := state.constants.get(x.value):
                    sym = Constant(con)
                else:
                    sym = x
                    state.variables.append(sym)
                if i == var_amt - 1:
                    sym = do_op(sym)
                expr = Mul(expr, sym)
            return expr
        else:
            assert isinstance(variables, (Constant, Variable))
            return do_op(variables)

    @staticmethod
    @pg.production("un : ADD group", precedence='UNOP')
    @pg.production("un : SUB group", precedence='UNOP')

    @pg.production("expr : ADD group", precedence='UNOP')
    @pg.production("expr : SUB group", precedence='UNOP')
    def unop(_, p: list[Token], /) -> UnaryOp:
        return {
            'ADD': Pos,
            'SUB': Neg,
        }[p[0].gettokentype()](p[1])

    @staticmethod
    @pg.production("un : ADD un", precedence='UNOP')
    @pg.production("un : SUB un", precedence='UNOP')

    @pg.production("expr : ADD un", precedence='UNOP')
    @pg.production("expr : SUB un", precedence='UNOP')
    def unop_chain(_, p: list[Token], /) -> UnaryOp:
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