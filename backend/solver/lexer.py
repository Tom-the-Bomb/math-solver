from rply import LexerGenerator as Generator

__all__ = ('LexerGenerator',)

class LexerGenerator(Generator):
    def __init__(self, /) -> None:
        super().__init__()
        self.add_rules()

    def add_rules(self, /) -> None:
        self.ignore(r'\s+')

        self.add_basic()
        self.add_operations()
        self.add_relational()
        self.add_groupers()

    def add_relational(self, /, *, inequality: bool = True) -> None:
        self.add('EQ', '=')
        if inequality:
            self.add('LT', '<')
            self.add('GT', '>')

    def add_basic(self, /) -> None:
        self.add('NUMBER', r'([0-9]+(\.[0-9]*)?|\.[0-9]+)')
        self.add('IDENT', r'[a-zA-Z]+')

    def add_operations(self) -> None:
        self.add('ADD', r'\+')
        self.add('SUB', '-')
        self.add('MUL', r'\*')
        self.add('DIV', '/')
        self.add('POW', r'\^')
        self.add('SUBSCRIPT', '_')
        self.add('FAC', '!')
        self.add('MOD', '%')

    def add_groupers(
        self, /,
        *,
        brace: bool = True,
    ) -> None:
        if round:
            self.add('LBRACK', r'\(|\[')
            self.add('RBRACK', r'\)|\]')
        if brace:
            self.add('LBRACE', r'\{')
            self.add('RBRACE', r'\}')