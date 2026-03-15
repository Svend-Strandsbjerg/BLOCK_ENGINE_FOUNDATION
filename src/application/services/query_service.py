from __future__ import annotations

from src.application.services.mappers import DomainReadModelMapper, OperationResultMapper
from src.application.services.read_models import (
    BlockLocationView,
    BlockView,
    ContainerSnapshotView,
    FrameworkVersionView,
)
from src.application.services.state import BlockFrameworkState
from src.domain.common.value_objects import BlockId, ContainerId
from src.domain.operations.result import OperationResult


class FrameworkQueryService:
    """Lightweight query service for deterministic UI-ready reads."""

    def __init__(self, state: BlockFrameworkState) -> None:
        self._state = state

    def get_container_snapshot(self, container_id: ContainerId) -> ContainerSnapshotView:
        if container_id not in self._state.containers:
            raise ValueError(f"Container {container_id} does not exist")
        return DomainReadModelMapper.to_container_snapshot_view(self._state, container_id)

    def list_blocks_for_container(self, container_id: ContainerId) -> list[BlockView]:
        snapshot = self.get_container_snapshot(container_id)
        return [DomainReadModelMapper.to_block_view(self._state, BlockId(item.block_id)) for item in snapshot.blocks]

    def get_block_location(self, block_id: BlockId) -> BlockLocationView:
        if block_id not in self._state.blocks:
            raise ValueError(f"Block {block_id} does not exist")
        return DomainReadModelMapper.to_block_location_view(self._state, block_id)

    def get_framework_version(self) -> FrameworkVersionView:
        return FrameworkVersionView(version=self._state.version)

    @staticmethod
    def get_operation_update_payload(result: OperationResult) -> dict[str, object]:
        return OperationResultMapper.to_external_dict(result)
