from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class OperationRejection:
    code: str
    message: str
    entity_ids: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
