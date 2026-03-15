import unittest

from src.application.command_handlers.handler import CommandHandler
from src.application.services.query_service import FrameworkQueryService
from src.application.services.state import BlockFrameworkState
from src.domain.commands.models import CreateBlock, CreateContainer, MoveBlock, PlaceBlock
from src.domain.block.models import BlockState
from src.domain.common.value_objects import BlockId, ContainerId, OperationId, OperationMetadata, SequencePosition


class PositioningAndQueryLayerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = BlockFrameworkState()
        self.handler = CommandHandler()

    @staticmethod
    def _metadata(op_id: str) -> OperationMetadata:
        return OperationMetadata(operation_id=OperationId(op_id), source="test", user_or_system="tester")

    def test_sequence_position_strategy_normalizes_order_deterministically(self) -> None:
        self.handler.apply(
            self.state,
            CreateContainer(metadata=self._metadata("op-c"), container_id=ContainerId("c1"), container_type="generic"),
        )
        self.handler.apply(
            self.state,
            CreateBlock(metadata=self._metadata("op-b1"), block_id=BlockId("b1"), block_type="generic"),
        )
        self.handler.apply(
            self.state,
            CreateBlock(metadata=self._metadata("op-b2"), block_id=BlockId("b2"), block_type="generic"),
        )
        self.handler.apply(
            self.state,
            PlaceBlock(
                metadata=self._metadata("op-p1"),
                block_id=BlockId("b1"),
                container_id=ContainerId("c1"),
                position=SequencePosition(order_index=10),
            ),
        )
        self.handler.apply(
            self.state,
            PlaceBlock(
                metadata=self._metadata("op-p2"),
                block_id=BlockId("b2"),
                container_id=ContainerId("c1"),
                position=SequencePosition(order_index=0),
            ),
        )

        query = FrameworkQueryService(self.state)
        container_snapshot = query.get_container_snapshot(ContainerId("c1"))

        self.assertEqual(["b2", "b1"], [item.block_id for item in container_snapshot.blocks])
        self.assertEqual([0, 1], [item.order_index for item in container_snapshot.blocks])

    def test_query_service_returns_version_and_operation_payload(self) -> None:
        self.handler.apply(
            self.state,
            CreateContainer(metadata=self._metadata("op-c1"), container_id=ContainerId("c1"), container_type="generic"),
        )
        self.handler.apply(
            self.state,
            CreateContainer(metadata=self._metadata("op-c2"), container_id=ContainerId("c2"), container_type="generic"),
        )
        self.handler.apply(
            self.state,
            CreateBlock(metadata=self._metadata("op-b"), block_id=BlockId("b1"), block_type="generic"),
        )
        self.handler.apply(
            self.state,
            PlaceBlock(
                metadata=self._metadata("op-p"),
                block_id=BlockId("b1"),
                container_id=ContainerId("c1"),
                position=SequencePosition(order_index=0),
            ),
        )

        move_result = self.handler.apply(
            self.state,
            MoveBlock(
                metadata=self._metadata("op-move"),
                block_id=BlockId("b1"),
                target_container_id=ContainerId("c2"),
                target_position=SequencePosition(order_index=0),
            ),
        )

        query = FrameworkQueryService(self.state)
        version = query.get_framework_version()
        block_location = query.get_block_location(BlockId("b1"))
        update_payload = query.get_operation_update_payload(move_result)

        self.assertEqual(self.state.version, version.version)
        self.assertEqual("c2", block_location.container_id)
        self.assertEqual(["b1"], update_payload["affected_block_ids"])
        self.assertEqual(["c1", "c2"], update_payload["affected_container_ids"])


    def test_query_service_exposes_block_state_without_interpretation(self) -> None:
        self.handler.apply(
            self.state,
            CreateContainer(metadata=self._metadata("op-c"), container_id=ContainerId("c1"), container_type="generic"),
        )
        self.handler.apply(
            self.state,
            CreateBlock(
                metadata=self._metadata("op-b"),
                block_id=BlockId("b1"),
                block_type="generic",
                state=BlockState("planned"),
            ),
        )
        self.handler.apply(
            self.state,
            PlaceBlock(
                metadata=self._metadata("op-p"),
                block_id=BlockId("b1"),
                container_id=ContainerId("c1"),
                position=SequencePosition(order_index=0),
            ),
        )

        query = FrameworkQueryService(self.state)
        block_view = query.list_blocks_for_container(ContainerId("c1"))[0]

        self.assertEqual("planned", block_view.state)


if __name__ == "__main__":
    unittest.main()
