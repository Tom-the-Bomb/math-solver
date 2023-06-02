from typing import Optional
from dataclasses import dataclass

__all__ = (
    'SolveSchema',
    'SolveResponse',
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
    latex: str
    raw: str
    parsed: str