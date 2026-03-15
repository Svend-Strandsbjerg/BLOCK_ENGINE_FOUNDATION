from __future__ import annotations

from dataclasses import dataclass, field

from src.domain.aggregates.container_aggregate import ContainerAggregate
from src.domain.block.models import Block
from src.domain.common.value_objects import BlockId, ContainerId


@dataclass(slots=True)
class BlockFrameworkState:
    """Deterministic in-memory state snapshot."""

    blocks: dict[BlockId, Block] = field(default_factory=dict)
    containers: dict[ContainerId, ContainerAggregate] = field(default_factory=dict)
    block_locations: dict[BlockId, ContainerId] = field(default_factory=dict)
    version: int = 0

    def increment_version(self) -> None:
        self.version += 1
