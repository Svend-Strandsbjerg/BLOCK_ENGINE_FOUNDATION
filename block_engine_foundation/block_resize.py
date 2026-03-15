from __future__ import annotations

from typing import Literal, TypedDict


class ResizeResult(TypedDict):
    start: float
    extent: float


def resize_placement(*, start: float, extent: float, delta: float, direction: Literal["forward", "backward"]) -> ResizeResult:
    """Apply generic geometric resize semantics."""

    if extent <= 0:
        raise ValueError("extent must be positive")

    if direction == "forward":
        new_start = start
        new_extent = extent + delta
    elif direction == "backward":
        new_start = start + delta
        new_extent = extent - delta
    else:
        raise ValueError("direction must be 'forward' or 'backward'")

    if new_extent <= 0:
        raise ValueError("resize operation produced non-positive extent")

    return {"start": new_start, "extent": new_extent}
