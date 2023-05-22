from .solve import Solver
from sympy import pprint

pprint(Solver().solve("x^2=-1"))
pprint(Solver().solve("x^2=1"))
pprint(Solver().solve("1=2*sin(x)+1"))