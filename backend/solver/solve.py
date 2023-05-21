from .parser import Parser

class Solver:
    def __init__(self, /) -> None:
        self.parser = Parser()

    def evaluate(self, equation: str) -> None:
        print(self.parser.parse(equation).eval())
