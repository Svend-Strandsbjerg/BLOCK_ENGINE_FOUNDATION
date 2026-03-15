from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.domain.common.value_objects import ContainerId, OperationMetadata
from src.domain.events.models import DomainEvent
from src.domain.operations.rejection import OperationRejection


@dataclass(frozen=True, slots=True)
class BlockLocationChange:
    block_id: str
    previous_container_id: str | None
    current_container_id: str | None


@dataclass(frozen=True, slots=True)
class OperationResult:
    success: bool
    metadata: OperationMetadata
    events: list[DomainEvent] = field(default_factory=list)
    rejections: list[OperationRejection] = field(default_factory=list)
    affected_block_ids: list[str] = field(default_factory=list)
    affected_container_ids: list[str] = field(default_factory=list)
    location_changes: list[BlockLocationChange] = field(default_factory=list)
    trace: dict[str, Any] = field(default_factory=dict)
    version: int | None = None

    @property
    def violations(self) -> list[str]:
        return [rejection.message for rejection in self.rejections]

    @staticmethod
    def failed(metadata: OperationMetadata, rejections: list[OperationRejection]) -> "OperationResult":
        return OperationResult(success=False, metadata=metadata, rejections=rejections)


def container_ids(*container_ids: ContainerId | None) -> list[str]:
    return [str(container_id) for container_id in container_ids if container_id is not None]
