
__all__ = (
    'NotAFunction',
    'CantGetProperty',
)

class NotAFunction(Exception):
    def __init__(self, provided: str, /) -> None:
        super().__init__(f'Invalid function syntax: {provided}\nCorrect Ex: f(x) = x^2')

class CantGetProperty(Exception):
    def __init__(self, property: str, /) -> None:
        super().__init__(f'Unable to retrieve <{property}> from provided function / expression')
