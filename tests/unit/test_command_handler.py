import unittest

from src.application.command_handlers.handler import CommandHandler
from src.application.services.state import BlockFrameworkState
from src.domain.commands.models import (
    CreateBlock,
    CreateContainer,
    MoveBlock,
    PlaceBlock,
    UpdateBlock,
)
from src.domain.common.value_objects import (
    BlockId,
    ContainerId,
    OperationId,
    OperationMetadata,
    SequencePosition,
)
from src.domain.events.models import BlockCreated, BlockMoved


class CommandHandlerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = BlockFrameworkState()
        self.handler = CommandHandler()

    @staticmethod
    def _metadata(op_id: str) -> OperationMetadata:
        return OperationMetadata(operation_id=OperationId(op_id), source="test", user_or_system="tester")

    def test_applies_create_and_move_flow_with_domain_events(self) -> None:
        self.handler.apply(
            self.state,
            CreateContainer(
                metadata=self._metadata("op-1"),
                container_id=ContainerId("c1"),
                container_type="generic",
            ),
        )
        self.handler.apply(
            self.state,
            CreateContainer(
                metadata=self._metadata("op-2"),
                container_id=ContainerId("c2"),
                container_type="generic",
            ),
        )
        create_result = self.handler.apply(
            self.state,
            CreateBlock(
                metadata=self._metadata("op-3"),
                block_id=BlockId("b1"),
                block_type="task",
                payload={"value": 5},
            ),
        )
        self.handler.apply(
            self.state,
            PlaceBlock(
                metadata=self._metadata("op-4"),
                block_id=BlockId("b1"),
                container_id=ContainerId("c1"),
                position=SequencePosition(order_index=0),
            ),
        )
        move_result = self.handler.apply(
            self.state,
            MoveBlock(
                metadata=self._metadata("op-5"),
                block_id=BlockId("b1"),
                target_container_id=ContainerId("c2"),
                target_position=SequencePosition(order_index=0),
            ),
        )

        self.assertIsInstance(create_result.events[0], BlockCreated)
        self.assertIsInstance(move_result.events[0], BlockMoved)
        self.assertEqual([BlockId("b1")], self.state.containers[ContainerId("c2")].block_order)
        self.assertEqual(ContainerId("c2"), self.state.block_locations[BlockId("b1")])

    def test_update_block_metadata(self) -> None:
        self.handler.apply(
            self.state,
            CreateContainer(
                metadata=self._metadata("op-1"),
                container_id=ContainerId("c1"),
                container_type="generic",
            ),
        )
        self.handler.apply(
            self.state,
            CreateBlock(
                metadata=self._metadata("op-2"),
                block_id=BlockId("b1"),
                block_type="task",
            ),
        )

        update_result = self.handler.apply(
            self.state,
            UpdateBlock(
                metadata=self._metadata("op-3"),
                block_id=BlockId("b1"),
                metadata_patch={"priority": "high"},
            ),
        )

        self.assertTrue(update_result.success)
        self.assertEqual("high", self.state.blocks[BlockId("b1")].metadata["priority"])


if __name__ == "__main__":
    unittest.main()
