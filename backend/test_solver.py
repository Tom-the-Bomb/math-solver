from solver import Solver

def test_parsing() -> None:
    equations = (
        "[2y]2sin(2[x])",
        "1 - 2 + -x + -3 - 4 + 5x - +0! != 7 % 2",
        "2log_2(x + 1)(y - pi) >= e",
        "1 + 2x - 3x - 9x^2 - 7 = 3xyz2",
        "[-inf, x + 1)",
    )

    for equation in equations:
        print(equation, '|', Solver(equation).parsed_equation)


def test_functions() -> None:
    print(
        Solver(
            'ax^2 + f(2g(x)) + 2c',
            functions=['f(x) = 2cx!', 'g(x) = 2x'],
            constants={'c': 5},
        ).parsed_equation
    )

def test_properties() -> None:
    print(
        Solver('x^2 + 4x + 4').factored
    )

if __name__ == '__main__':
    test_parsing()
    test_functions()
    test_properties()