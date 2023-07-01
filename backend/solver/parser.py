from __future__ import annotations

from typing import (
    TYPE_CHECKING, Any,
    TypeAlias, ClassVar, NoReturn, Optional, Callable, Iterable,
)
from decimal import Decimal
import inspect

from rply import Token, ParserGenerator
from rply.lexer import SourcePosition, LexingError
from sympy.logic.boolalg import BooleanAtom
from sympy import (
    limit,
    N, E, I, pi, GoldenRatio, oo,
    functions as func_mod,
    NumberSymbol,
)

from .lexer import LexerGenerator
from .exceptions import *
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
Constants: TypeAlias = dict[str, Decimal | NumberSymbol | int] | dict[str, float]

def _to_camel_case(string: str) -> str:
    """Converts identifier from snake_case to camelCase

    * Required for function names to not conflict with subscripts on function names
    """
    terms = iter(string.split('_'))
    return next(terms).lower() + ''.join(t.title() for t in terms)

class Parser:
    GREEK_LETTERS: ClassVar[list[str]] = [
        'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta',
        'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'omicron', 'pi', 'rho',
        'sigma', 'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega',
        'Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta',
        'Iota', 'Kappa', 'Lambda', 'Mu', 'Nu', 'Xi', 'Omicron', 'Pi', 'Rho',
        'Sigma', 'Tau', 'Upsilon', 'Phi', 'Chi', 'Psi', 'Omega',
    ]

    lg: ClassVar[LexerGenerator] = LexerGenerator()
    pg: ClassVar[ParserGenerator] = ParserGenerator(
        [
            token.name for token in lg.rules
        ],
        precedence=[
            ('right', ['UNOP']),
            ('left', ['ADD', 'SUB']),
            ('left', ['MUL', 'DIV', 'MOD', 'AT']),
            ('left', ['IMPL_MUL']),
            ('right', ['POW']),
            ('left', ['FAC']),
        ]
    )

    def __init__(
        self, /,
        *,
        is_parsing_function: Optional[bool] = False,
        functions: Optional[Functions] = None,
        constants: Optional[Constants] = None,

        max_number: Optional[float] = None,
        max_exponent: Optional[float] = None,
        max_factorial: Optional[float] = None,
    ) -> None:
        self.is_parsing_function = is_parsing_function

        self._max_number = max_number if max_number is not None else float('inf')
        self._max_exponent = max_exponent if max_exponent is not None else float('inf')
        self._max_factorial = max_factorial if max_factorial is not None else float('inf')

        def _round(x: Expr, place: Optional[int] = None) -> Expr:
            try:
                return round(x, place) # type: ignore
            except TypeError:
                return x

        self.functions = {
            'eval': N,
            'lmit': limit,
            'rt': func_mod.root,
            'rad': lambda x: x * (pi / 180),
            'deg': lambda x: x * (180 / pi),
            'ceil': func_mod.ceiling,
            'round': _round,
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
            'infty': oo,
            'oo': oo,

            'π': pi,
            'τ': 2 * pi,
            'φ': GoldenRatio,
            'Φ': GoldenRatio,
            '∞': oo,
        },
            **({k: Decimal(str(v)) if isinstance(v, float) else v for k, v in constants.items()}
            if constants else {})
        }

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
    def defined_function(state: Parser, p: list[list[Ast]]) -> DefinedFunction | BinaryOp | BooleanResult:
        assert isinstance(name := p[0][0], Token)
        assert isinstance(expr := p[-1], Ast)

        if not state.is_parsing_function:
            func = Parser.fx(state, [p[0]])
            return Parser.equation(state, [func, *p[1:]]) # type: ignore

        f_name = name.getstr()
        arguments: list[Ast] = p[0][-1] if isinstance(p[0][-1], list) else [p[0][-1]]
        return DefinedFunction(f_name, arguments, expr)

    @staticmethod
    @pg.production('interval : LBRACK expr COMMA expr RBRACK')
    @pg.production('interval : LBRACK expr COMMA expr RPAREN')

    @pg.production('interval : LPAREN expr COMMA expr RBRACK')
    @pg.production('interval : LPAREN expr COMMA expr RPAREN')
    def domain_interval(_, p: list[Token]) -> Interval:
        assert isinstance(p[1], Ast)
        assert isinstance(p[-2], Ast)

        return Interval(p[0].getstr(), p[1], p[-2], p[-1].getstr())

    @staticmethod
    @pg.production('equation : IDENT PIPE interval')
    @pg.production('equation : interval')
    def domain_compound_interval(_, p: list[Interval]) -> Interval:
        if len(p) == 1:
            return p[0]
        else:
            assert isinstance(p[0], Token)
            return CompoundInterval(p[0].getstr(), p[2])

    @staticmethod
    @pg.production('equation : expr')
    @pg.production('equation : expr EQ expr')
    @pg.production('equation : expr NE expr')
    @pg.production('equation : expr LT expr')
    @pg.production('equation : expr LT EQ expr')
    @pg.production('equation : expr GT expr')
    @pg.production('equation : expr GT EQ expr')
    def equation(state: Parser, p: list[Token], /) -> BinaryOp | BooleanResult:
        if len(p) == 1 and isinstance(p[0], Ast):
            conditional = Eq(p[0], Number('0', state._max_number))
        else:
            conditional: Conditional = {
                ('EQ', None): Eq,
                ('NE', None): Ne,
                ('LT', None): Lt,
                ('LT', 'EQ'): Le,
                ('GT', None): Gt,
                ('GT', 'EQ'): Ge,
            }[(p[1].gettokentype(), getattr(p[2], 'gettokentype', lambda: None)())](p[0], p[-1])

        if isinstance(conditional.eval(), BooleanAtom):
            return BooleanResult(conditional)
        return conditional

    @staticmethod
    @pg.production('expr : group')
    def group(_, p: list[Ast], /) -> Ast:
        return p[0]

    @staticmethod
    @pg.production('group : combination call', precedence='IMPL_MUL')
    def fx_combinations(state: Parser, p: list[Ast]) -> Function | BinaryOp:
        call: list[Ast] = p[-1] if isinstance(p[-1], list) else [p[-1]] # type: ignore
        assert isinstance(t := p[0], BinaryOp)

        if isinstance(t.left, (Constant, Variable)) and isinstance(t.right, (Constant, Variable)):
            left = t.left.value if isinstance(t.left, Variable) else t.left.ident
            right = t.right.value if isinstance(t.right, Variable) else t.right.ident
        else:
            return Mul(t, call[0])
        f1 = state.functions.get(left)
        f2 = state.functions.get(right)
        if f1 is not None and f2 is not None:
            if isinstance(t, At):
                return Function(f1, Function(f2, *call))
            return t.__class__(Function(f1, *call), Function(f2, *call))
        elif len(call) > 1:
            raise InvalidFunctionCall(left, right)
        else:
            return Mul(t, call[0])

    @staticmethod
    @pg.production('group : ROOT root', precedence='IMPL_MUL')
    def implicit_mul(_, p: list[Mul], /) -> Root:
        left = p[1].left
        right = p[1].right
        return Root(left, right)

    @staticmethod
    @pg.production('group : group group', precedence='IMPL_MUL')
    @pg.production('root : group group', precedence='IMPL_MUL')
    def custom_root(_, p: list[Ast], /) -> Mul:
        return Mul(p[0], p[1])

    @staticmethod
    @pg.production('group : NUMBER')
    def number(state: Parser, p: list[Token], /) -> Number:
        return Number(p[0].getstr(), state._max_number)

    @staticmethod
    @pg.production('expr : PIPE expr PIPE')
    def abs_val(_, p: list[Ast]) -> Abs:
        return Abs(p[1])

    @staticmethod
    @pg.production('group : LPAREN expr RPAREN')
    @pg.production('group : LBRACK expr RBRACK')
    @pg.production('group : LBRACE expr RBRACE')
    def paren(_, p: list[Ast], /) -> Ast:
        return p[1] if len(p) == 3 else p[0]

    @pg.production('combination : LPAREN binop RPAREN')
    def combination(_, p: list[Ast], /) -> Ast:
        return p[1]

    @pg.production('group : combination')
    def combination_group(_, p: list[Ast], /) -> Ast:
        return p[0]

    @staticmethod
    @pg.production('group : group FAC')
    def factorial(state: Parser, p: list[Ast], /) -> Fac:
        return Fac(p[0], state._max_factorial)

    @staticmethod
    @pg.production('group : LIMIT SUBSCRIPT LPAREN group ARROW expr RPAREN group')
    def limit(_, p: list[Ast], /) -> Limit:
        return Limit(p[3], p[5], p[-1])

    @staticmethod
    @pg.production('expr : binop')
    def binop_expr(_, p: list[Ast]) -> Ast:
        return p[0]

    @staticmethod
    @pg.production('binop : expr ADD expr')
    @pg.production('binop : expr SUB expr')
    @pg.production('binop : expr MUL expr')
    @pg.production('binop : expr DIV expr')
    @pg.production('binop : expr MOD expr')
    @pg.production('binop : expr AT expr')

    @pg.production('group : group POW group')
    def binop(state: Parser, p: list[Ast], /) -> BinaryOp:
        assert isinstance(tok := p[1], Token)
        typ = tok.gettokentype()
        if typ == 'POW':
            return Pow(p[0], p[2], state._max_exponent)
        return {
            'ADD': Add,
            'SUB': Sub,
            'MUL': Mul,
            'DIV': Div,
            'MOD': Mod,
            'AT': At,
        }[typ](p[0], p[2])

    @staticmethod
    @pg.production('expr : SUM SUBSCRIPT LPAREN var EQ group RPAREN POW group group')
    @pg.production('expr : PROD SUBSCRIPT LPAREN var EQ group RPAREN POW group group')
    def summation_product(_, p: list[Ast], /) -> Summation:
        if isinstance(variables := p[3], map):
            variable = Variable(''.join(x.value for x in variables))
        elif isinstance(constant := p[3], Constant):
            variable = Variable(constant.ident)
        else:
            assert isinstance(p[3], Variable)
            variable = p[3]

        assert isinstance(tok := p[0], Token)
        if tok.gettokentype() == 'SUM':
            return Summation(variable, p[5], p[-2], p[-1])
        else:
            return Product(variable, p[5], p[-2], p[-1])

    @pg.production('arguments : expr')
    def arguments_start(_, p: list[Ast]) -> Ast:
        return p[0]

    @pg.production('arguments : arguments COMMA expr')
    def arguments(_, p: list[list[Ast]]) -> list[Ast]:
        assert isinstance(p[-1], Ast)
        return p[0] + [p[-1]] if isinstance(p[0], list) else [p[0]] + [p[-1]] # type: ignore

    @pg.production('call : LPAREN RPAREN')
    @pg.production('call : LPAREN arguments RPAREN')
    def arguments_call(_, p: list[list[Ast]]) -> list[Ast]:
        return p[1] if len(p) == 3 else []

    @staticmethod
    @pg.production('func : IDENT call')

    @pg.production('func : IDENT SUBSCRIPT NUMBER call')
    @pg.production('func : IDENT SUBSCRIPT IDENT call')

    @pg.production('func : IDENT SUBSCRIPT LPAREN expr RPAREN call')
    def func(_, p: list[Ast]) -> list[Ast]:
        return p

    @staticmethod
    @pg.production('group : func')
    def fx(state: Parser, _p: list[list[Ast]], /) -> Function | Mul:
        p = _p[0]
        call = p[-1] if isinstance(p[-1], list) else [p[-1]]

        assert isinstance(p[0], Token)
        ident = p[0].getstr()

        subscript = None
        if len(p) == 6:
            subscript = p[3]
        elif len(p) == 4 and isinstance(tok := p[2], Token):
            subscript = {
                'NUMBER': Parser.number,
                'IDENT': lambda s, p: Parser.multi_var(s, [Parser.variable(s, p)]),
            }[tok.gettokentype()](state, [tok])

        if (f := state.functions.get(ident)) is not None:
            arguments = tuple(call)
            if len(p) in (4, 6) and subscript:
                arguments += (subscript,)
            return Function(f, *arguments)

        if len(p) in (4, 6) and subscript:
            ident += f'_{subscript.eval()}'
        if len(call) > 1:
            raise InvalidFunctionCall(ident)
        return Mul(
            Parser.multi_var(
                state,
                [Parser.variable(state, [p[0]])],
            ),
            p[-1],
        )

    @staticmethod
    @pg.production('var : IDENT')
    @pg.production('var : IDENT SUBSCRIPT NUMBER')
    @pg.production('var : IDENT SUBSCRIPT IDENT')
    def variable(state: Parser, p: list[Token], /) -> Constant | Variable | Iterable[Variable]:
        ident: str = p[0].getstr()
        if len(p) == 3:
            ident += f'_{p[-1].getstr()}'

        if (x := state.constants.get(ident)) is not None:
            return Constant(ident, x)

        raw = p[0].getstr()
        if len(ident) == 1 or raw in state.GREEK_LETTERS:
            var = Variable(ident)
            state.variables.append(var)
            return var

        if len(p) == 3:
            sub: str = p[-1].getstr()
            if p[-1].gettokentype() == 'NUMBER':
                return map(Variable, [*raw[:-1], raw[-1] + f'_{sub}'])
            return map(Variable, [*raw[:-1], raw[-1] + f'_{sub[0]}', *sub[1:]])
        else:
            return map(Variable, ident)

    @pg.production('group : var POW group')
    @pg.production('group : var FAC')
    @pg.production('group : var')
    def multi_var(state: Parser, p: list[Ast | Iterable[Variable]]) -> Number | Constant | Variable | Mul | Fac | Pow:
        def do_op(var: Constant | Variable) -> Constant | Variable | Fac | Pow:
            match len(p):
                case 2:
                    return Fac(var, state._max_factorial)
                case 3:
                    assert isinstance(p[2], Ast)
                    return Pow(var, p[2], state._max_exponent)
                case _:
                    return var

        variables = p[0]
        if isinstance(variables, map):
            var_amt = len(variables := tuple(variables))

            expr = Number('1', state._max_number)
            for i, x in enumerate(variables):
                x: Variable
                if (con := state.constants.get(x.value)) is not None:
                    sym = Constant(x.value, con)
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