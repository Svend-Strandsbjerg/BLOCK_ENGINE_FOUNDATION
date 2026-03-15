from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True, slots=True)
class OperationMetadata:
    operation_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "unknown"
    user_or_system: str = "system"


@dataclass(frozen=True, slots=True)
class Command:
    metadata: OperationMetadata


@dataclass(frozen=True, slots=True)
class CreateContainer(Command):
    container_id: str
    container_type: str
    metadata_patch: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CreateBlock(Command):
    block_id: str
    block_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    metadata_patch: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class UpdateBlock(Command):
    block_id: str
    metadata_patch: dict[str, Any]


@dataclass(frozen=True, slots=True)
class PlaceBlock(Command):
    block_id: str
    container_id: str
    index: int


@dataclass(frozen=True, slots=True)
class MoveBlock(Command):
    block_id: str
    target_container_id: str
    target_index: int


@dataclass(frozen=True, slots=True)
class RemoveBlock(Command):
    block_id: str
