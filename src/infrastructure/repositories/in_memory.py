from __future__ import annotations

from copy import deepcopy

from src.application.services.state import BlockFrameworkState
from src.infrastructure.repositories.base import StateRepository


class InMemoryStateRepository(StateRepository):
    def __init__(self) -> None:
        self._state = BlockFrameworkState()

    def load(self) -> BlockFrameworkState:
        return deepcopy(self._state)

    def save(self, state: BlockFrameworkState) -> None:
        self._state = deepcopy(state)
