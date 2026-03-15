from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.domain.common.value_objects import OperationMetadata
from src.domain.events.models import DomainEvent


@dataclass(frozen=True, slots=True)
class OperationResult:
    success: bool
    metadata: OperationMetadata
    events: list[DomainEvent] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)
    affected_entities: list[str] = field(default_factory=list)
    trace: dict[str, Any] = field(default_factory=dict)
    version: int | None = None

    @staticmethod
    def failed(metadata: OperationMetadata, violations: list[str]) -> "OperationResult":
        return OperationResult(success=False, metadata=metadata, violations=violations)
