from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Position:
    """Deterministic index position within a container."""

    order_index: int

    def __post_init__(self) -> None:
        if self.order_index < 0:
            raise ValueError("order_index must be non-negative")
