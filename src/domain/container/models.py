from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.domain.common.value_objects import ContainerId


@dataclass(slots=True)
class Container:
    """Container aggregate root metadata."""

    container_id: ContainerId
    container_type: str
    metadata: dict[str, Any] = field(default_factory=dict)
    version: int = 0
