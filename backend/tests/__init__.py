from solver import Solver

print(Solver('(f + g)(x)', functions=['f(x) = x', 'g(x) = 2']).parsed_equation)