from __future__ import annotations

from dataclasses import dataclass

from src.domain.common.value_objects import BlockId, ContainerId, OperationMetadata, Position


@dataclass(frozen=True, slots=True)
class DomainEvent:
    metadata: OperationMetadata


@dataclass(frozen=True, slots=True)
class BlockCreated(DomainEvent):
    block_id: BlockId


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
