from __future__ import annotations

from abc import ABC, abstractmethod

from src.application.services.state import BlockFrameworkState
from src.domain.common.value_objects import BlockId, ContainerId, SequencePosition


class PlacementPolicy(ABC):
    @abstractmethod
    def validate(self, state: BlockFrameworkState, block_id: BlockId, container_id: ContainerId, position: SequencePosition) -> list[str]:
        raise NotImplementedError


class MovementPolicy(ABC):
    @abstractmethod
    def validate(
        self,
        state: BlockFrameworkState,
        block_id: BlockId,
        source_container_id: ContainerId,
        target_container_id: ContainerId,
        position: SequencePosition,
    ) -> list[str]:
        raise NotImplementedError


class PositionConflictPolicy(ABC):
    @abstractmethod
    def validate(self, state: BlockFrameworkState, container_id: ContainerId, position: SequencePosition) -> list[str]:
        raise NotImplementedError


class ContainerConstraintPolicy(ABC):
    @abstractmethod
    def validate(self, state: BlockFrameworkState, container_id: ContainerId) -> list[str]:
        raise NotImplementedError


class DefaultPlacementPolicy(PlacementPolicy):
    def validate(self, state: BlockFrameworkState, block_id: BlockId, container_id: ContainerId, position: SequencePosition) -> list[str]:
        violations: list[str] = []
        if block_id in state.block_locations:
            violations.append(f"Block {block_id} is already placed")
        if container_id not in state.containers:
            violations.append(f"Container {container_id} does not exist")
        return violations


class DefaultMovementPolicy(MovementPolicy):
    def validate(
        self,
        state: BlockFrameworkState,
        block_id: BlockId,
        source_container_id: ContainerId,
        target_container_id: ContainerId,
        position: SequencePosition,
    ) -> list[str]:
        violations: list[str] = []
        if source_container_id not in state.containers:
            violations.append(f"Source container {source_container_id} does not exist")
        if target_container_id not in state.containers:
            violations.append(f"Target container {target_container_id} does not exist")
        return violations


class DefaultPositionConflictPolicy(PositionConflictPolicy):
    def validate(self, state: BlockFrameworkState, container_id: ContainerId, position: SequencePosition) -> list[str]:
        return []


class DefaultContainerConstraintPolicy(ContainerConstraintPolicy):
    def validate(self, state: BlockFrameworkState, container_id: ContainerId) -> list[str]:
        return []
