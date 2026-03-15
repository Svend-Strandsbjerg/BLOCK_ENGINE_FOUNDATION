from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BlockState:
    """Opaque lifecycle marker managed by consumers of the foundation."""

    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("BlockState value cannot be empty")

    def __str__(self) -> str:
        return self.value
