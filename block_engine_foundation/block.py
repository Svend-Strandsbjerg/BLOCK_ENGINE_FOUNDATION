from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .block_extent import BlockExtent


@dataclass(slots=True)
class Block:
    """Domain-agnostic canonical block model."""

    id: str
    state: str
    extent: BlockExtent
    payload: dict[str, Any] = field(default_factory=dict)
    start_time: float = 0.0

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("Block id cannot be empty")
        if not self.state.strip():
            raise ValueError("Block state cannot be empty")
