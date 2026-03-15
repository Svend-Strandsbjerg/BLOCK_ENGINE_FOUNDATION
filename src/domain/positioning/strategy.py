from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.common.value_objects import BlockId, Position, SequencePosition


class PositionStrategy(ABC):
    """Defines how a container stores and orders block positions."""

    name: str

    @abstractmethod
    def supports(self, position: Position) -> bool:
        raise NotImplementedError

    @abstractmethod
    def set_position(
        self,
        positions: dict[BlockId, Position],
        block_id: BlockId,
        position: Position,
    ) -> dict[BlockId, Position]:
        raise NotImplementedError

    @abstractmethod
    def ordered_blocks(self, positions: dict[BlockId, Position]) -> list[BlockId]:
        raise NotImplementedError


class SequencePositionStrategy(PositionStrategy):
    """Deterministic strategy based on normalized integer order indexes."""

    name = "sequence"

    def supports(self, position: Position) -> bool:
        return isinstance(position, SequencePosition) and position.strategy == self.name

    def set_position(
        self,
        positions: dict[BlockId, Position],
        block_id: BlockId,
        position: Position,
    ) -> dict[BlockId, Position]:
        if not self.supports(position):
            raise ValueError(f"Unsupported position for strategy '{self.name}'")

        sequence_position = position
        normalized = self._normalize(positions)
        existing_order = self.ordered_blocks(normalized)
        if block_id in existing_order:
            existing_order.remove(block_id)

        target_index = max(0, min(sequence_position.order_index, len(existing_order)))
        existing_order.insert(target_index, block_id)
        return {
            current_block_id: SequencePosition(order_index=index)
            for index, current_block_id in enumerate(existing_order)
        }

    def ordered_blocks(self, positions: dict[BlockId, Position]) -> list[BlockId]:
        normalized = self._normalize(positions)
        ordered_pairs = sorted(
            normalized.items(),
            key=lambda entry: (entry[1].order_index, entry[0].value),
        )
        return [block_id for block_id, _ in ordered_pairs]

    def _normalize(self, positions: dict[BlockId, Position]) -> dict[BlockId, SequencePosition]:
        if not positions:
            return {}
        sequence_pairs = []
        for block_id, candidate in positions.items():
            if not self.supports(candidate):
                raise ValueError(f"Unsupported position for strategy '{self.name}'")
            sequence_pairs.append((block_id, candidate))

        ordered_pairs = sorted(
            sequence_pairs,
            key=lambda entry: (entry[1].order_index, entry[0].value),
        )
        return {
            block_id: SequencePosition(order_index=index)
            for index, (block_id, _) in enumerate(ordered_pairs)
        }
