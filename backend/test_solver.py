from solver import Solver

def test() -> None:
    equations = (
        "[2y]2sin(2[x])",
        "1 - 2 + -x + -3 - 4 + 5x - +0! != 7 % 2",
        "2log_2(x + 1)(y - pi) >= e",
        "1 + 2x - 3x - 9x^2 - 7 = 3xyz2",
        "[-inf, x + 1)",
    )

    for equation in equations:
        print(equation, '|', Solver(equation).parsed_equation)

if __name__ == '__main__':
    print(Solver('f(x) + 1', functions=['f(x) = x^2']).parsed_equation)