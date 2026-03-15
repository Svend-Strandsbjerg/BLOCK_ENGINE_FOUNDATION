from __future__ import annotations

from dataclasses import dataclass, field

from src.domain.common.value_objects import BlockId, ContainerId, SequencePosition
from src.domain.container.models import Container


@dataclass(slots=True)
class ContainerAggregate:
    container: Container
    block_order: list[BlockId] = field(default_factory=list)

    @property
    def container_id(self) -> ContainerId:
        return self.container.container_id

    @property
    def version(self) -> int:
        return self.container.version

    def increment_version(self) -> None:
        self.container.version += 1

    def add_block(self, block_id: BlockId, position: SequencePosition) -> None:
        bounded_index = max(0, min(position.order_index, len(self.block_order)))
        self.block_order.insert(bounded_index, block_id)

    def remove_block(self, block_id: BlockId) -> None:
        self.block_order.remove(block_id)
