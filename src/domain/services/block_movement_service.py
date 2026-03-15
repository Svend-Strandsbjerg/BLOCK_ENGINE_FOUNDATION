from __future__ import annotations

from src.application.services.state import BlockFrameworkState


class BlockMovementService:
    """Pure movement logic for ordering and relocating blocks."""

    @staticmethod
    def place(state: BlockFrameworkState, block_id: str, container_id: str, index: int) -> None:
        BlockMovementService._ensure_block_exists(state, block_id)
        BlockMovementService._ensure_container_exists(state, container_id)

        if block_id in state.block_locations:
            raise ValueError(f"Block {block_id} is already placed")

        order = state.container_block_order.setdefault(container_id, [])
        bounded_index = max(0, min(index, len(order)))
        order.insert(bounded_index, block_id)
        state.block_locations[block_id] = container_id

    @staticmethod
    def move(state: BlockFrameworkState, block_id: str, target_container_id: str, target_index: int) -> None:
        BlockMovementService._ensure_block_exists(state, block_id)
        BlockMovementService._ensure_container_exists(state, target_container_id)

        source_container_id = state.block_locations.get(block_id)
        if source_container_id is None:
            raise ValueError(f"Block {block_id} is not placed")

        source_order = state.container_block_order[source_container_id]
        source_order.remove(block_id)

        target_order = state.container_block_order.setdefault(target_container_id, [])
        bounded_index = max(0, min(target_index, len(target_order)))
        target_order.insert(bounded_index, block_id)
        state.block_locations[block_id] = target_container_id

    @staticmethod
    def remove(state: BlockFrameworkState, block_id: str) -> None:
        BlockMovementService._ensure_block_exists(state, block_id)

        container_id = state.block_locations.pop(block_id, None)
        if container_id:
            state.container_block_order[container_id].remove(block_id)

        del state.blocks[block_id]

    @staticmethod
    def list_blocks(state: BlockFrameworkState, container_id: str) -> list[str]:
        BlockMovementService._ensure_container_exists(state, container_id)
        return list(state.container_block_order.get(container_id, []))

    @staticmethod
    def _ensure_block_exists(state: BlockFrameworkState, block_id: str) -> None:
        if block_id not in state.blocks:
            raise ValueError(f"Block {block_id} does not exist")

    @staticmethod
    def _ensure_container_exists(state: BlockFrameworkState, container_id: str) -> None:
        if container_id not in state.containers:
            raise ValueError(f"Container {container_id} does not exist")
