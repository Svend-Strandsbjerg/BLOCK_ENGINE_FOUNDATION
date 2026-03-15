from __future__ import annotations

from abc import ABC, abstractmethod

from src.application.services.state import BlockFrameworkState
from src.domain.block.models import BlockExtent, BlockState
from src.domain.common.value_objects import BlockId, ContainerId, Position
from src.domain.operations.rejection import OperationRejection


class PlacementPolicy(ABC):
    @abstractmethod
    def validate(
        self,
        state: BlockFrameworkState,
        block_id: BlockId,
        container_id: ContainerId,
        position: Position,
    ) -> list[OperationRejection]:
        raise NotImplementedError


class MovementPolicy(ABC):
    @abstractmethod
    def validate(
        self,
        state: BlockFrameworkState,
        block_id: BlockId,
        source_container_id: ContainerId,
        target_container_id: ContainerId,
        position: Position,
    ) -> list[OperationRejection]:
        raise NotImplementedError


class PositionConflictPolicy(ABC):
    @abstractmethod
    def validate(
        self,
        state: BlockFrameworkState,
        container_id: ContainerId,
        position: Position,
    ) -> list[OperationRejection]:
        raise NotImplementedError


class ContainerConstraintPolicy(ABC):
    @abstractmethod
    def validate(self, state: BlockFrameworkState, container_id: ContainerId) -> list[OperationRejection]:
        raise NotImplementedError


class StateTransitionPolicy(ABC):
    @abstractmethod
    def validate(
        self,
        current_state: BlockState | None,
        target_state: BlockState,
    ) -> list[OperationRejection]:
        raise NotImplementedError


class BlockExtentPolicy(ABC):
    @abstractmethod
    def validate(
        self,
        current_extent: BlockExtent | None,
        target_extent: BlockExtent,
    ) -> list[OperationRejection]:
        raise NotImplementedError


class DefaultPlacementPolicy(PlacementPolicy):
    def validate(
        self,
        state: BlockFrameworkState,
        block_id: BlockId,
        container_id: ContainerId,
        position: Position,
    ) -> list[OperationRejection]:
        rejections: list[OperationRejection] = []
        if block_id in state.block_locations:
            rejections.append(
                OperationRejection(
                    code="block.already_placed",
                    message=f"Block {block_id} is already placed",
                    entity_ids=[str(block_id)],
                )
            )
        if container_id not in state.containers:
            rejections.append(
                OperationRejection(
                    code="container.not_found",
                    message=f"Container {container_id} does not exist",
                    entity_ids=[str(container_id)],
                )
            )
        return rejections


class DefaultMovementPolicy(MovementPolicy):
    def validate(
        self,
        state: BlockFrameworkState,
        block_id: BlockId,
        source_container_id: ContainerId,
        target_container_id: ContainerId,
        position: Position,
    ) -> list[OperationRejection]:
        rejections: list[OperationRejection] = []
        if source_container_id not in state.containers:
            rejections.append(
                OperationRejection(
                    code="container.source_not_found",
                    message=f"Source container {source_container_id} does not exist",
                    entity_ids=[str(source_container_id)],
                )
            )
        if target_container_id not in state.containers:
            rejections.append(
                OperationRejection(
                    code="container.target_not_found",
                    message=f"Target container {target_container_id} does not exist",
                    entity_ids=[str(target_container_id)],
                )
            )
        return rejections


class DefaultPositionConflictPolicy(PositionConflictPolicy):
    def validate(
        self,
        state: BlockFrameworkState,
        container_id: ContainerId,
        position: Position,
    ) -> list[OperationRejection]:
        return []


class DefaultContainerConstraintPolicy(ContainerConstraintPolicy):
    def validate(self, state: BlockFrameworkState, container_id: ContainerId) -> list[OperationRejection]:
        return []


class DefaultStateTransitionPolicy(StateTransitionPolicy):
    def validate(
        self,
        current_state: BlockState | None,
        target_state: BlockState,
    ) -> list[OperationRejection]:
        return []


class DefaultBlockExtentPolicy(BlockExtentPolicy):
    def validate(
        self,
        current_extent: BlockExtent | None,
        target_extent: BlockExtent,
    ) -> list[OperationRejection]:
        return []
