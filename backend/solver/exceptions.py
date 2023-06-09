
__all__ = (
    'SolverException',
    'InvalidDomainParsed',
    'InvalidFunctionArgument',
    'InvalidFunctionCall',
    'NotAFunction',
    'CantGetProperty',
)

class SolverException(Exception):
    ...

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