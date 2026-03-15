from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Container:
    """Ordered environment where blocks live."""

    container_id: str
    container_type: str
    metadata: dict[str, Any] = field(default_factory=dict)
