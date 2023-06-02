from quart import Quart
from quart_schema import (
    QuartSchema,
    validate_request,
    validate_response
)

from .solver import Solver

from .models import *

app = Quart(__name__)
QuartSchema(app)

@app.route('/solve', methods=['POST'])
@validate_request(SolveSchema)
@validate_response(SolveResponse)
async def post_solve(data: SolveSchema) -> SolveResponse:
    solver = Solver(
        data.equation,
        domain=data.domain,
        solve_for=data.solve_for,
        functions=data.functions,
        constants=data.constants,
    )
    
    return SolveResponse(
        latex=solver.latex_solution,
        raw=solver.ascii_parsed_solution,
        parsed=solver.parsed_solution,
    )

def run(debug: bool = False) -> None:
    app.run(debug=debug)