from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class BlockId:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("BlockId cannot be empty")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ContainerId:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("ContainerId cannot be empty")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class OperationId:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("OperationId cannot be empty")

    def __str__(self) -> str:
        return self.value


class Position(Protocol):
    strategy: str


@dataclass(frozen=True, slots=True)
class SequencePosition:
    order_index: int
    strategy: str = "sequence"

    def __post_init__(self) -> None:
        if self.order_index < 0:
            raise ValueError("order_index must be non-negative")


@dataclass(frozen=True, slots=True)
class OperationMetadata:
    operation_id: OperationId
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "unknown"
    user_or_system: str = "system"
    idempotency_key: str | None = None
    context: dict[str, Any] = field(default_factory=dict)
