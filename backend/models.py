from typing import Optional
from dataclasses import dataclass

__all__ = (
    'SolveSchema',
    'SolveResponse',
    'Error',
)

@dataclass
class SolveSchema:
    equation: str
    domain: Optional[str] = None
    solve_for: Optional[str] = None
    functions: Optional[list[str]] = None
    constants: Optional[dict[str, float]] = None

@dataclass
class SolveResponse:
    domain: str
    range: str
    equation: str
    simplified_equation: str
    latex_solution: str
    raw_solution: str
    parsed_solution: str
    derivative: str

@dataclass
class Error:
    error: str