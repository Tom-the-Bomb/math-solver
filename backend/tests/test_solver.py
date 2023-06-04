from solver import Solver

__all__ = (
    'test_parsing',
    'test_functions',
    'test_domain',
    'test_properties',
)

def test_parsing() -> None:
    equations = (
        "[2y]2sin(2[x])",
        "1 - 2 + -x + -3 - 4 + 5x - +0! != 7 % 2",
        "2log_2(x + 1)(y - pi) >= e",
        "1 + 2x - 3x - 9x^2 - 7 = 3xyz2",
        'lim(2x + a, x, 0) + 1'
        "[-inf, x + 1)",
    )

    print()
    for equation in equations:
        print(equation, '|', Solver(equation).parsed_equation)

def test_functions() -> None:
    print()
    print(
        Solver(
            'ax^2 + f(2g(x)) + 2c - h()',
            functions=['f(x) = 2cx!', 'g(x) = 2x', 'h() = 7(1)'],
            constants={'c': 5},
        ).parsed_equation
    )

def test_domain() -> None:
    print()
    print(
        Solver(
            'sin(x)',
            domain='[0, 2pi]',
        ).parsed_solution()
    )

def test_properties() -> None:
    solver = Solver('x^2 + 4x + 4')
    print('\nfactored:', solver.factored)
    print('{}: {}'.format(*tuple(solver.max_min.items())[0]))
    print('domain:', solver.domain)
    print('range:', solver.range)

if __name__ == '__main__':
    test_parsing()
    test_functions()
    test_properties()
    test_domain()