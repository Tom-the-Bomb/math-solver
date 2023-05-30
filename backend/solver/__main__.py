from . import Solver

try:
    print(Solver("1 + 2x").parsed_equation)
finally:
    print("-"*30)
    print(Solver("1 + 2 + 3").parsed_equation)