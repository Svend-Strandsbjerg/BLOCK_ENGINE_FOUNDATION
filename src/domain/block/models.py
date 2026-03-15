from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.domain.common.value_objects import BlockId


@dataclass(slots=True)
class Block:
    """Domain-agnostic unit of information managed by the framework."""

    block_id: BlockId
    block_type: str
    metadata: dict[str, Any] = field(default_factory=dict)
    payload: dict[str, Any] = field(default_factory=dict)
    version: int = 0
