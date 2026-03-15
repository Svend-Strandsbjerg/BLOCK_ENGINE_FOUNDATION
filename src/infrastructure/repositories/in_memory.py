from __future__ import annotations

from copy import deepcopy

from src.application.services.state import BlockFrameworkState
from src.infrastructure.repositories.base import PersistedSnapshot, StateRepository


class InMemoryStateRepository(StateRepository):
    def __init__(self) -> None:
        self._snapshot = PersistedSnapshot(state=BlockFrameworkState(), version=0)

    def load_snapshot(self) -> PersistedSnapshot:
        return PersistedSnapshot(state=deepcopy(self._snapshot.state), version=self._snapshot.version)

    def save_snapshot(self, state: BlockFrameworkState, expected_version: int | None = None) -> PersistedSnapshot:
        if expected_version is not None and expected_version != self._snapshot.version:
            raise ValueError(
                f"Version mismatch: expected {expected_version}, current {self._snapshot.version}"
            )
        new_snapshot = PersistedSnapshot(state=deepcopy(state), version=state.version)
        self._snapshot = new_snapshot
        return PersistedSnapshot(state=deepcopy(new_snapshot.state), version=new_snapshot.version)
