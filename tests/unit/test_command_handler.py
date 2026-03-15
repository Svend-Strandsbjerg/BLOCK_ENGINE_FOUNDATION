import unittest

from src.application.command_handlers.handler import CommandHandler
from src.application.services.state import BlockFrameworkState
from src.domain.commands.models import (
    CreateBlock,
    CreateContainer,
    MoveBlock,
    OperationMetadata,
    PlaceBlock,
    UpdateBlock,
)


class CommandHandlerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = BlockFrameworkState()
        self.handler = CommandHandler()

    @staticmethod
    def _metadata(op_id: str) -> OperationMetadata:
        return OperationMetadata(operation_id=op_id, source="test", user_or_system="tester")

    def test_applies_create_and_move_flow(self) -> None:
        self.handler.apply(
            self.state,
            CreateContainer(
                metadata=self._metadata("op-1"),
                container_id="c1",
                container_type="swimlane",
            ),
        )
        self.handler.apply(
            self.state,
            CreateContainer(
                metadata=self._metadata("op-2"),
                container_id="c2",
                container_type="queue",
            ),
        )
        self.handler.apply(
            self.state,
            CreateBlock(
                metadata=self._metadata("op-3"),
                block_id="b1",
                block_type="task",
                payload={"value": 5},
            ),
        )
        self.handler.apply(
            self.state,
            PlaceBlock(metadata=self._metadata("op-4"), block_id="b1", container_id="c1", index=0),
        )
        self.handler.apply(
            self.state,
            MoveBlock(
                metadata=self._metadata("op-5"),
                block_id="b1",
                target_container_id="c2",
                target_index=0,
            ),
        )

        self.assertEqual(["b1"], self.state.container_block_order["c2"])
        self.assertEqual("c2", self.state.block_locations["b1"])

    def test_update_block_metadata(self) -> None:
        self.handler.apply(
            self.state,
            CreateContainer(
                metadata=self._metadata("op-1"),
                container_id="c1",
                container_type="swimlane",
            ),
        )
        self.handler.apply(
            self.state,
            CreateBlock(
                metadata=self._metadata("op-2"),
                block_id="b1",
                block_type="task",
            ),
        )

        self.handler.apply(
            self.state,
            UpdateBlock(
                metadata=self._metadata("op-3"),
                block_id="b1",
                metadata_patch={"priority": "high"},
            ),
        )

        self.assertEqual("high", self.state.blocks["b1"].metadata["priority"])


if __name__ == "__main__":
    unittest.main()
