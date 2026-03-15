from __future__ import annotations

from abc import ABC, abstractmethod

from src.application.services.state import BlockFrameworkState


class StateRepository(ABC):
    """Repository abstraction for persisting deterministic state snapshots."""

    @abstractmethod
    def load(self) -> BlockFrameworkState:
        raise NotImplementedError

    @abstractmethod
    def save(self, state: BlockFrameworkState) -> None:
        raise NotImplementedError
