from __future__ import annotations

from src.application.services.state import BlockFrameworkState
from src.domain.common.value_objects import BlockId, ContainerId, OperationMetadata, Position
from src.domain.events.models import BlockMoved, BlockPlaced, BlockRemoved, BlockReordered
from src.domain.operations.rejection import OperationRejection
from src.domain.operations.result import BlockLocationChange, OperationResult, container_ids
from src.domain.policies.movement_policies import (
    ContainerConstraintPolicy,
    DefaultContainerConstraintPolicy,
    DefaultMovementPolicy,
    DefaultPlacementPolicy,
    DefaultPositionConflictPolicy,
    MovementPolicy,
    PlacementPolicy,
    PositionConflictPolicy,
)


class BlockMovementService:
    """Orchestrates movement use-cases by delegating decisions to policies."""

    def __init__(
        self,
        placement_policy: PlacementPolicy | None = None,
        movement_policy: MovementPolicy | None = None,
        position_conflict_policy: PositionConflictPolicy | None = None,
        container_constraint_policy: ContainerConstraintPolicy | None = None,
    ) -> None:
        self._placement_policy = placement_policy or DefaultPlacementPolicy()
        self._movement_policy = movement_policy or DefaultMovementPolicy()
        self._position_conflict_policy = position_conflict_policy or DefaultPositionConflictPolicy()
        self._container_constraint_policy = container_constraint_policy or DefaultContainerConstraintPolicy()

    def place(
        self,
        state: BlockFrameworkState,
        block_id: BlockId,
        container_id: ContainerId,
        position: Position,
        metadata: OperationMetadata,
    ) -> OperationResult:
        rejections = self._ensure_block_exists(state, block_id)
        rejections.extend(self._placement_policy.validate(state, block_id, container_id, position))
        rejections.extend(self._position_conflict_policy.validate(state, container_id, position))
        rejections.extend(self._container_constraint_policy.validate(state, container_id))
        if rejections:
            return OperationResult.failed(metadata, rejections)

        container = state.containers[container_id]
        if not container.positioning_strategy.supports(position):
            return OperationResult.failed(
                metadata,
                [
                    OperationRejection(
                        code="position.unsupported_strategy",
                        message=f"Container {container_id} does not support position strategy {position.strategy}",
                        entity_ids=[str(container_id)],
                    )
                ],
            )

        previous_container_id = state.block_locations.get(block_id)
        container.set_block_position(block_id, position)
        state.block_locations[block_id] = container_id
        container.increment_version()
        state.increment_version()
        return OperationResult(
            success=True,
            metadata=metadata,
            events=[BlockPlaced(metadata=metadata, block_id=block_id, container_id=container_id, position=position)],
            affected_block_ids=[str(block_id)],
            affected_container_ids=[str(container_id)],
            location_changes=[
                BlockLocationChange(
                    block_id=str(block_id),
                    previous_container_id=str(previous_container_id) if previous_container_id else None,
                    current_container_id=str(container_id),
                )
            ],
            version=state.version,
        )

    def move(
        self,
        state: BlockFrameworkState,
        block_id: BlockId,
        target_container_id: ContainerId,
        target_position: Position,
        metadata: OperationMetadata,
    ) -> OperationResult:
        rejections = self._ensure_block_exists(state, block_id)
        source_container_id = state.block_locations.get(block_id)
        if source_container_id is None:
            rejections.append(
                OperationRejection(
                    code="block.not_placed",
                    message=f"Block {block_id} is not placed",
                    entity_ids=[str(block_id)],
                )
            )
            return OperationResult.failed(metadata, rejections)

        rejections.extend(
            self._movement_policy.validate(
                state,
                block_id,
                source_container_id,
                target_container_id,
                target_position,
            )
        )
        rejections.extend(self._position_conflict_policy.validate(state, target_container_id, target_position))
        rejections.extend(self._container_constraint_policy.validate(state, target_container_id))

        target_container = state.containers.get(target_container_id)
        if target_container and not target_container.positioning_strategy.supports(target_position):
            rejections.append(
                OperationRejection(
                    code="position.unsupported_strategy",
                    message=f"Container {target_container_id} does not support position strategy {target_position.strategy}",
                    entity_ids=[str(target_container_id)],
                )
            )
        if rejections:
            return OperationResult.failed(metadata, rejections)

        source_container = state.containers[source_container_id]
        target_container = state.containers[target_container_id]

        source_container.remove_block(block_id)
        target_container.set_block_position(block_id, target_position)
        state.block_locations[block_id] = target_container_id
        source_container.increment_version()
        if source_container_id != target_container_id:
            target_container.increment_version()
        state.increment_version()

        event = (
            BlockReordered(
                metadata=metadata,
                block_id=block_id,
                container_id=target_container_id,
                position=target_position,
            )
            if source_container_id == target_container_id
            else BlockMoved(
                metadata=metadata,
                block_id=block_id,
                source_container_id=source_container_id,
                target_container_id=target_container_id,
                position=target_position,
            )
        )
        return OperationResult(
            success=True,
            metadata=metadata,
            events=[event],
            affected_block_ids=[str(block_id)],
            affected_container_ids=container_ids(source_container_id, target_container_id),
            location_changes=[
                BlockLocationChange(
                    block_id=str(block_id),
                    previous_container_id=str(source_container_id),
                    current_container_id=str(target_container_id),
                )
            ],
            version=state.version,
        )

    def remove(self, state: BlockFrameworkState, block_id: BlockId, metadata: OperationMetadata) -> OperationResult:
        rejections = self._ensure_block_exists(state, block_id)
        if rejections:
            return OperationResult.failed(metadata, rejections)

        container_id = state.block_locations.pop(block_id, None)
        if container_id:
            container = state.containers[container_id]
            container.remove_block(block_id)
            container.increment_version()

        del state.blocks[block_id]
        state.increment_version()
        return OperationResult(
            success=True,
            metadata=metadata,
            events=[BlockRemoved(metadata=metadata, block_id=block_id, container_id=container_id)],
            affected_block_ids=[str(block_id)],
            affected_container_ids=container_ids(container_id),
            location_changes=[
                BlockLocationChange(
                    block_id=str(block_id),
                    previous_container_id=str(container_id) if container_id else None,
                    current_container_id=None,
                )
            ],
            version=state.version,
        )

    @staticmethod
    def list_blocks(state: BlockFrameworkState, container_id: ContainerId) -> list[BlockId]:
        if container_id not in state.containers:
            raise ValueError(f"Container {container_id} does not exist")
        return list(state.containers[container_id].block_order)

    @staticmethod
    def _ensure_block_exists(state: BlockFrameworkState, block_id: BlockId) -> list[OperationRejection]:
        if block_id not in state.blocks:
            return [
                OperationRejection(
                    code="block.not_found",
                    message=f"Block {block_id} does not exist",
                    entity_ids=[str(block_id)],
                )
            ]
        return []
