import unittest

from src.application.services.state import BlockFrameworkState
from src.domain.aggregates.container_aggregate import ContainerAggregate
from src.domain.block.models import Block
from src.domain.common.value_objects import (
    BlockId,
    ContainerId,
    OperationId,
    OperationMetadata,
    SequencePosition,
)
from src.domain.container.models import Container
from src.domain.events.models import BlockMoved, BlockReordered
from src.domain.services.block_movement_service import BlockMovementService


class BlockMovementServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = BlockMovementService()
        self.state = BlockFrameworkState(
            blocks={
                BlockId("b1"): Block(block_id=BlockId("b1"), block_type="generic"),
                BlockId("b2"): Block(block_id=BlockId("b2"), block_type="generic"),
            },
            containers={
                ContainerId("c1"): ContainerAggregate(
                    container=Container(container_id=ContainerId("c1"), container_type="generic")
                ),
                ContainerId("c2"): ContainerAggregate(
                    container=Container(container_id=ContainerId("c2"), container_type="generic")
                ),
            },
        )

    @staticmethod
    def _metadata(op_id: str) -> OperationMetadata:
        return OperationMetadata(operation_id=OperationId(op_id), source="test", user_or_system="tester")

    def test_place_block_returns_sync_friendly_result_and_event(self) -> None:
        result = self.service.place(
            self.state,
            BlockId("b1"),
            ContainerId("c1"),
            SequencePosition(order_index=50),
            self._metadata("op-place"),
        )

        self.assertTrue(result.success)
        self.assertEqual(1, len(result.events))
        self.assertEqual(["b1"], result.affected_block_ids)
        self.assertEqual(["c1"], result.affected_container_ids)
        self.assertEqual("c1", result.location_changes[0].current_container_id)
        self.assertEqual([BlockId("b1")], self.state.containers[ContainerId("c1")].block_order)
        self.assertEqual(ContainerId("c1"), self.state.block_locations[BlockId("b1")])

    def test_move_block_between_containers_emits_block_moved(self) -> None:
        self.service.place(
            self.state,
            BlockId("b1"),
            ContainerId("c1"),
            SequencePosition(order_index=0),
            self._metadata("op-place-1"),
        )
        self.service.place(
            self.state,
            BlockId("b2"),
            ContainerId("c1"),
            SequencePosition(order_index=1),
            self._metadata("op-place-2"),
        )

        result = self.service.move(
            self.state,
            BlockId("b1"),
            ContainerId("c2"),
            SequencePosition(order_index=0),
            self._metadata("op-move"),
        )

        self.assertTrue(result.success)
        self.assertIsInstance(result.events[0], BlockMoved)
        self.assertEqual(["c1", "c2"], result.affected_container_ids)
        self.assertEqual([BlockId("b2")], self.state.containers[ContainerId("c1")].block_order)
        self.assertEqual([BlockId("b1")], self.state.containers[ContainerId("c2")].block_order)

    def test_move_within_same_container_emits_block_reordered(self) -> None:
        self.service.place(
            self.state,
            BlockId("b1"),
            ContainerId("c1"),
            SequencePosition(order_index=0),
            self._metadata("op-place-1"),
        )
        self.service.place(
            self.state,
            BlockId("b2"),
            ContainerId("c1"),
            SequencePosition(order_index=1),
            self._metadata("op-place-2"),
        )

        result = self.service.move(
            self.state,
            BlockId("b1"),
            ContainerId("c1"),
            SequencePosition(order_index=1),
            self._metadata("op-reorder"),
        )

        self.assertTrue(result.success)
        self.assertIsInstance(result.events[0], BlockReordered)
        self.assertEqual(
            [BlockId("b2"), BlockId("b1")],
            self.state.containers[ContainerId("c1")].block_order,
        )


if __name__ == "__main__":
    unittest.main()
