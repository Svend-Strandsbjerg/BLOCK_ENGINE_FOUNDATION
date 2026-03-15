from __future__ import annotations

from src.application.services.read_models import (
    BlockLocationView,
    BlockView,
    ContainerBlockView,
    ContainerSnapshotView,
)
from src.application.services.state import BlockFrameworkState
from src.domain.common.value_objects import BlockId, ContainerId
from src.domain.operations.result import OperationResult


class DomainReadModelMapper:
    """Mapping boundary from internal domain objects to external read contracts."""

    @staticmethod
    def to_block_view(state: BlockFrameworkState, block_id: BlockId) -> BlockView:
        block = state.blocks[block_id]
        return BlockView(
            block_id=str(block.block_id),
            block_type=block.block_type,
            state=str(block.state) if block.state else None,
            metadata=dict(block.metadata),
            payload=dict(block.payload),
            version=block.version,
        )

    @staticmethod
    def to_container_snapshot_view(state: BlockFrameworkState, container_id: ContainerId) -> ContainerSnapshotView:
        container = state.containers[container_id]
        block_views = [
            ContainerBlockView(block_id=str(block_id), order_index=index)
            for index, block_id in enumerate(container.block_order)
        ]
        return ContainerSnapshotView(
            container_id=str(container.container_id),
            container_type=container.container.container_type,
            strategy=container.strategy_name,
            version=container.version,
            blocks=block_views,
        )

    @staticmethod
    def to_block_location_view(state: BlockFrameworkState, block_id: BlockId) -> BlockLocationView:
        container_id = state.block_locations.get(block_id)
        return BlockLocationView(
            block_id=str(block_id),
            container_id=str(container_id) if container_id else None,
        )


class OperationResultMapper:
    @staticmethod
    def to_external_dict(result: OperationResult) -> dict[str, object]:
        return {
            "success": result.success,
            "operation_id": str(result.metadata.operation_id),
            "version": result.version,
            "affected_block_ids": list(result.affected_block_ids),
            "affected_container_ids": list(result.affected_container_ids),
            "location_changes": [
                {
                    "block_id": change.block_id,
                    "previous_container_id": change.previous_container_id,
                    "current_container_id": change.current_container_id,
                }
                for change in result.location_changes
            ],
            "rejections": [
                {
                    "code": rejection.code,
                    "message": rejection.message,
                    "entity_ids": list(rejection.entity_ids),
                    "context": dict(rejection.context),
                }
                for rejection in result.rejections
            ],
            "event_types": [event.__class__.__name__ for event in result.events],
        }
