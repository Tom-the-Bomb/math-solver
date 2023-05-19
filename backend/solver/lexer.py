from rply import LexerGenerator as Generator

class LexerGenerator(Generator):
    def __init__(self) -> None:
        super().__init__()
        self.add_rules()

    def add_rules(self) -> None:
        self.add('NUMBER', r'([0-9]+(\.[0-9]*)?|\.[0-9]+)')
        

    def add_operations(self) -> None:
        self.add('ADD', r'\+')
        self.add('SUB', '-')
        self.add('MUL', r'\*')
        self.add('DIV', '/')
        self.add('POW', r'\^')
        self.add('FAC', '!')
        self.add('MOD', '%')

    def add_groupers(
        self,
        *,
        round: bool = True,
        square: bool = True,
        brace: bool = True,
    ) -> None:
        if round:
            self.add('LPAREN', r'\(')
            self.add('RPAREN', r'\)')
        if square:
            self.add('LBRACK', r'\[')
            self.add('RBRACK', r'\]')
        if brace:
            self.add('LBRACE', r'\{')
            self.add('RBRACE', r'\}')