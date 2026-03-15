from __future__ import annotations

from dataclasses import dataclass, field

from src.domain.common.value_objects import BlockId, ContainerId, Position
from src.domain.container.models import Container
from src.domain.positioning.strategy import PositionStrategy, SequencePositionStrategy


@dataclass(slots=True)
class ContainerAggregate:
    container: Container
    positioning_strategy: PositionStrategy = field(default_factory=SequencePositionStrategy)
    block_positions: dict[BlockId, Position] = field(default_factory=dict)

    @property
    def container_id(self) -> ContainerId:
        return self.container.container_id

    @property
    def version(self) -> int:
        return self.container.version

    @property
    def strategy_name(self) -> str:
        return self.positioning_strategy.name

    @property
    def block_order(self) -> list[BlockId]:
        return self.positioning_strategy.ordered_blocks(self.block_positions)

    def increment_version(self) -> None:
        self.container.version += 1

    def set_block_position(self, block_id: BlockId, position: Position) -> None:
        self.block_positions = self.positioning_strategy.set_position(self.block_positions, block_id, position)

    def remove_block(self, block_id: BlockId) -> None:
        if block_id not in self.block_positions:
            return
        del self.block_positions[block_id]
        ordered = self.block_order
        self.block_positions = {
            current_block_id: self.block_positions[current_block_id]
            for current_block_id in ordered
        }

    def position_for(self, block_id: BlockId) -> Position | None:
        return self.block_positions.get(block_id)
