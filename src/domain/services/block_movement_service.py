from __future__ import annotations

from src.application.services.state import BlockFrameworkState
from src.domain.common.value_objects import BlockId, ContainerId, OperationMetadata, SequencePosition
from src.domain.events.models import BlockMoved, BlockPlaced, BlockRemoved, BlockReordered
from src.domain.operations.result import OperationResult
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
        position: SequencePosition,
        metadata: OperationMetadata,
    ) -> OperationResult:
        violations = self._ensure_block_exists(state, block_id)
        violations.extend(self._placement_policy.validate(state, block_id, container_id, position))
        violations.extend(self._position_conflict_policy.validate(state, container_id, position))
        violations.extend(self._container_constraint_policy.validate(state, container_id))
        if violations:
            return OperationResult.failed(metadata, violations)

        container = state.containers[container_id]
        container.add_block(block_id, position)
        state.block_locations[block_id] = container_id
        container.increment_version()
        state.increment_version()
        return OperationResult(
            success=True,
            metadata=metadata,
            events=[BlockPlaced(metadata=metadata, block_id=block_id, container_id=container_id, position=position)],
            affected_entities=[str(block_id), str(container_id)],
            version=state.version,
        )

    def move(
        self,
        state: BlockFrameworkState,
        block_id: BlockId,
        target_container_id: ContainerId,
        target_position: SequencePosition,
        metadata: OperationMetadata,
    ) -> OperationResult:
        violations = self._ensure_block_exists(state, block_id)
        source_container_id = state.block_locations.get(block_id)
        if source_container_id is None:
            violations.append(f"Block {block_id} is not placed")
            return OperationResult.failed(metadata, violations)

        violations.extend(
            self._movement_policy.validate(
                state,
                block_id,
                source_container_id,
                target_container_id,
                target_position,
            )
        )
        violations.extend(self._position_conflict_policy.validate(state, target_container_id, target_position))
        violations.extend(self._container_constraint_policy.validate(state, target_container_id))
        if violations:
            return OperationResult.failed(metadata, violations)

        source_container = state.containers[source_container_id]
        target_container = state.containers[target_container_id]

        source_container.remove_block(block_id)
        target_container.add_block(block_id, target_position)
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
            affected_entities=[str(block_id), str(source_container_id), str(target_container_id)],
            version=state.version,
        )

    def remove(self, state: BlockFrameworkState, block_id: BlockId, metadata: OperationMetadata) -> OperationResult:
        violations = self._ensure_block_exists(state, block_id)
        if violations:
            return OperationResult.failed(metadata, violations)

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
            affected_entities=[str(block_id)],
            version=state.version,
        )

    @staticmethod
    def list_blocks(state: BlockFrameworkState, container_id: ContainerId) -> list[BlockId]:
        if container_id not in state.containers:
            raise ValueError(f"Container {container_id} does not exist")
        return list(state.containers[container_id].block_order)

    @staticmethod
    def _ensure_block_exists(state: BlockFrameworkState, block_id: BlockId) -> list[str]:
        if block_id not in state.blocks:
            return [f"Block {block_id} does not exist"]
        return []
