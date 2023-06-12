from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar, Callable
import asyncio

from .models import SolveSchema
from .solver.exceptions import MathTimeout

if TYPE_CHECKING:
    R = TypeVar('R')

__all__ = ('run_threaded',)

async def run_threaded(
    func: Callable[[SolveSchema], R], /,
    argument: SolveSchema,
    *,
    timeout: float = 60.0,
) -> R:
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(func, argument),
            timeout=timeout,
        )
    except asyncio.TimeoutError as e:
        raise MathTimeout(timeout) from e