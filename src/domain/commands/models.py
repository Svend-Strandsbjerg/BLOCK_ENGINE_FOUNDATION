from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.domain.common.value_objects import BlockId, ContainerId, OperationMetadata, Position


@dataclass(frozen=True, slots=True)
class Command:
    metadata: OperationMetadata


@dataclass(frozen=True, slots=True)
class CreateContainer(Command):
    container_id: ContainerId
    container_type: str
    metadata_patch: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CreateBlock(Command):
    block_id: BlockId
    block_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    metadata_patch: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class UpdateBlock(Command):
    block_id: BlockId
    metadata_patch: dict[str, Any]


@dataclass(frozen=True, slots=True)
class PlaceBlock(Command):
    block_id: BlockId
    container_id: ContainerId
    position: Position


@dataclass(frozen=True, slots=True)
class MoveBlock(Command):
    block_id: BlockId
    target_container_id: ContainerId
    target_position: Position


@dataclass(frozen=True, slots=True)
class RemoveBlock(Command):
    block_id: BlockId
