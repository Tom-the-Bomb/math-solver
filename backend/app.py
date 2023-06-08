from datetime import timedelta

from quart import Quart
from quart_cors import cors
from quart_rate_limiter import RateLimiter, rate_limit
from quart_schema import (
    QuartSchema,
    validate_request,
    validate_response
)

from .solver import Solver

from .models import *
from .solver.exceptions import CantGetProperty

app = Quart(__name__)
cors(app, allow_origin="http://localhost:3000")
RateLimiter(app)
QuartSchema(app)

@app.route('/solve', methods=['POST'])
@validate_request(SolveSchema)
@validate_response(SolveResponse, status_code=200)
@validate_response(Error, status_code=500)
@rate_limit(3, timedelta(seconds=5))
async def post_solve(data: SolveSchema) -> SolveResponse | Error:
    try:
        solver = Solver(
            data.equation,
            domain=data.domain,
            solve_for=data.solve_for,
            functions=data.functions,
            constants=data.constants,
        )
        try:
            domain = solver.to_latex(solver.domain)
        except CantGetProperty:
            domain = r'\emptyset'
        try:
            range = solver.to_latex(solver.range)
        except CantGetProperty:
            range = r'\emptyset'
        return SolveResponse(
            domain=domain,
            range=range,
            equation=solver.to_latex(solver.parsed_equation),
            derivative=solver.to_latex(solver.derivative),
            simplified_equation=solver.to_latex(solver.simplify()),
            latex_solution=solver.to_latex(solver.solution),
            raw_solution=solver.ascii_parsed_solution(evaluate_bool=True),
            parsed_solution=solver.parsed_solution(evaluate_bool=True),
        ), 200
    except Exception as e:
        return Error(error=str(e)), 500

def run(debug: bool = False) -> None:
    app.run(debug=debug)