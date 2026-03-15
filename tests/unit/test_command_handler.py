import unittest

from src.application.command_handlers.handler import CommandHandler
from src.application.services.state import BlockFrameworkState
from src.domain.commands.models import (
    ChangeBlockState,
    CreateBlock,
    CreateContainer,
    MoveBlock,
    PlaceBlock,
    UpdateBlock,
)
from src.domain.block.models import BlockState
from src.domain.common.value_objects import (
    BlockId,
    ContainerId,
    OperationId,
    OperationMetadata,
    SequencePosition,
)
from src.domain.events.models import BlockCreated, BlockMoved, BlockStateChanged
from src.domain.operations.rejection import OperationRejection


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


    def test_change_block_state_emits_event_and_updates_block(self) -> None:
        self.handler.apply(
            self.state,
            CreateBlock(
                metadata=self._metadata("op-1"),
                block_id=BlockId("b1"),
                block_type="task",
                state=BlockState("planned"),
            ),
        )

        result = self.handler.apply(
            self.state,
            ChangeBlockState(
                metadata=self._metadata("op-2"),
                block_id=BlockId("b1"),
                state=BlockState("committed"),
            ),
        )

        self.assertTrue(result.success)
        self.assertIsInstance(result.events[0], BlockStateChanged)
        self.assertEqual("planned", str(result.events[0].previous_state))
        self.assertEqual("committed", str(result.events[0].current_state))
        self.assertEqual("committed", str(self.state.blocks[BlockId("b1")].state))

    def test_state_transition_policy_can_reject_state_change(self) -> None:
        class RejectPolicy:
            def validate(self, current_state, target_state):
                return [
                    OperationRejection(
                        code="state.transition_blocked",
                        message="blocked by policy",
                        entity_ids=["b1"],
                    )
                ]

        handler = CommandHandler(state_transition_policy=RejectPolicy())
        handler.apply(
            self.state,
            CreateBlock(
                metadata=self._metadata("op-1"),
                block_id=BlockId("b1"),
                block_type="task",
                state=BlockState("planned"),
            ),
        )

        result = handler.apply(
            self.state,
            ChangeBlockState(
                metadata=self._metadata("op-2"),
                block_id=BlockId("b1"),
                state=BlockState("approved"),
            ),
        )

        self.assertFalse(result.success)
        self.assertEqual("state.transition_blocked", result.rejections[0].code)
        self.assertEqual("planned", str(self.state.blocks[BlockId("b1")].state))

    def test_rejection_model_for_duplicate_block_is_structured(self) -> None:
        self.handler.apply(
            self.state,
            CreateBlock(
                metadata=self._metadata("op-1"),
                block_id=BlockId("b1"),
                block_type="task",
            ),
        )

        result = self.handler.apply(
            self.state,
            CreateBlock(
                metadata=self._metadata("op-2"),
                block_id=BlockId("b1"),
                block_type="task",
            ),
        )

        self.assertFalse(result.success)
        self.assertEqual("block.already_exists", result.rejections[0].code)
        self.assertEqual("Block b1 already exists", result.rejections[0].message)


if __name__ == "__main__":
    unittest.main()
