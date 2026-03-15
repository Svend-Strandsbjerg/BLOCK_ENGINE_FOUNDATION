from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.application.services.state import BlockFrameworkState


@dataclass(frozen=True, slots=True)
class PersistedSnapshot:
    state: BlockFrameworkState
    version: int


class StateRepository(ABC):
    """Repository abstraction for aggregate-aware deterministic snapshots."""

    @abstractmethod
    def load_snapshot(self) -> PersistedSnapshot:
        raise NotImplementedError

    @abstractmethod
    def save_snapshot(self, state: BlockFrameworkState, expected_version: int | None = None) -> PersistedSnapshot:
        raise NotImplementedError
