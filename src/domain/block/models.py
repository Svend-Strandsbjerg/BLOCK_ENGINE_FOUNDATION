from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.domain.common.value_objects import BlockId


@dataclass(frozen=True, slots=True)
class BlockState:
    """Generic state code for a block, interpreted by consuming applications."""

    code: str

    def __post_init__(self) -> None:
        if not self.code.strip():
            raise ValueError("BlockState code cannot be empty")

    def __str__(self) -> str:
        return self.code


@dataclass(slots=True)
class Block:
    """Domain-agnostic unit of information managed by the framework."""

    block_id: BlockId
    block_type: str
    state: BlockState | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    payload: dict[str, Any] = field(default_factory=dict)
    version: int = 0
