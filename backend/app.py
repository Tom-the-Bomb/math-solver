from __future__ import annotations

from typing import TypeAlias, TYPE_CHECKING
from datetime import timedelta
from io import BytesIO

from quart import Quart, Response, send_file
from quart_cors import cors
from quart_rate_limiter import RateLimiter, rate_limit
from quart_schema import (
    QuartSchema,
    validate_request,
    validate_response
)

from .solver import Solver
from .solver.exceptions import CantGetProperty

from .models import *
from .helpers import run_threaded

if TYPE_CHECKING:
    T_SolveResponse: TypeAlias = tuple[SolveResponse, int] | tuple[Error, int]

app = Quart(__name__)
cors(app, allow_origin="http://localhost:3000")
RateLimiter(app)
QuartSchema(app)

def do_solve(data: SolveSchema) -> T_SolveResponse:
    try:
        solver = Solver(
            data.equation,
            domain=data.domain,
            solve_for=data.solve_for,
            functions=data.functions,
            constants=data.constants,
        )
        try:
            domain = Solver.to_latex(solver.domain)
        except CantGetProperty:
            domain = r'\emptyset'
        try:
            range = Solver.to_latex(solver.range)
        except CantGetProperty:
            range = r'\emptyset'
        try:
            max_min = {k: Solver.to_latex(v) for k, v in solver.max_min.items()}
        except CantGetProperty:
            max_min = {'max': r'\infty', 'min': r'-\infty'}
        return SolveResponse(
            domain=domain,
            range=range,
            factored=Solver.to_latex(solver.factored),
            expanded=Solver.to_latex(solver.expanded),
            equation=Solver.to_latex(solver.parsed_equation),
            derivative=Solver.to_latex(solver.derivative),
            simplified_equation=Solver.to_latex(solver.simplify()),
            latex_solution=Solver.to_latex(solver.solution),
            raw_solution=solver.ascii_parsed_solution(evaluate_bool=True),
            parsed_solution=solver.parsed_solution(evaluate_bool=True),
            **max_min,
        ), 200
    except Exception as e:
        return Error(error=str(e)), 500

def do_graph(data: SolveSchema) -> BytesIO | tuple[Error, int]:
    try:
        solver = Solver(
            data.equation,
            domain=data.domain,
            solve_for=data.solve_for,
            functions=data.functions,
            constants=data.constants,
        )
        return solver.graph()
    except Exception as e:
        return Error(error=str(e)), 500

@app.route('/solve', methods=['POST'])
@validate_request(SolveSchema)
@validate_response(SolveResponse, status_code=200)
@validate_response(Error, status_code=500)
@rate_limit(3, timedelta(seconds=5))
async def post_solve(data: SolveSchema) -> T_SolveResponse:
    try:
        return await run_threaded(do_solve, data)
    except Exception as e:
        return Error(error=str(e)), 500

@app.route('/graph', methods=['POST'])
@validate_request(SolveSchema)
@validate_response(Error, status_code=500)
@rate_limit(3, timedelta(seconds=5))
async def post_graph(data: SolveSchema) -> Response | tuple[Error, int]:
    try:
        result = await run_threaded(do_graph, data)
    except Exception as e:
        return Error(error=str(e)), 500
    if isinstance(result, BytesIO):
        result = await send_file(result, mimetype='image/png')
    return result

def run(debug: bool = False) -> None:
    app.run(debug=debug)