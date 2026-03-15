from __future__ import annotations

from dataclasses import dataclass, field

from src.domain.block.models import Block
from src.domain.container.models import Container


@dataclass(slots=True)
class BlockFrameworkState:
    """Deterministic in-memory state snapshot."""

    blocks: dict[str, Block] = field(default_factory=dict)
    containers: dict[str, Container] = field(default_factory=dict)
    container_block_order: dict[str, list[str]] = field(default_factory=dict)
    block_locations: dict[str, str] = field(default_factory=dict)
