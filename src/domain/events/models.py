from __future__ import annotations

from dataclasses import dataclass

from src.domain.block.models import BlockExtent, BlockState
from src.domain.common.value_objects import BlockId, ContainerId, OperationMetadata, Position


@dataclass(frozen=True, slots=True)
class DomainEvent:
    metadata: OperationMetadata


@dataclass(frozen=True, slots=True)
class BlockCreated(DomainEvent):
    block_id: BlockId
    state: BlockState | None


@dataclass(frozen=True, slots=True)
class BlockStateChanged(DomainEvent):
    block_id: BlockId
    previous_state: BlockState | None
    current_state: BlockState


@dataclass(frozen=True, slots=True)
class BlockExtentChanged(DomainEvent):
    block_id: BlockId
    previous_extent: BlockExtent | None
    current_extent: BlockExtent


@dataclass(frozen=True, slots=True)
class BlockPlaced(DomainEvent):
    block_id: BlockId
    container_id: ContainerId
    position: Position


@dataclass(frozen=True, slots=True)
class BlockMoved(DomainEvent):
    block_id: BlockId
    source_container_id: ContainerId
    target_container_id: ContainerId
    position: Position


@dataclass(frozen=True, slots=True)
class BlockRemoved(DomainEvent):
    block_id: BlockId
    container_id: ContainerId | None


@dataclass(frozen=True, slots=True)
class BlockReordered(DomainEvent):
    block_id: BlockId
    container_id: ContainerId
    position: Position
