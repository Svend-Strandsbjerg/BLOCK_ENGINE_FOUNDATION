import unittest

from src.application.services.state import BlockFrameworkState
from src.domain.block.models import Block
from src.domain.container.models import Container
from src.domain.services.block_movement_service import BlockMovementService


class BlockMovementServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = BlockFrameworkState(
            blocks={
                "b1": Block(block_id="b1", block_type="generic"),
                "b2": Block(block_id="b2", block_type="generic"),
            },
            containers={
                "c1": Container(container_id="c1", container_type="swimlane"),
                "c2": Container(container_id="c2", container_type="queue"),
            },
            container_block_order={"c1": [], "c2": []},
        )

    def test_place_block_bounds_index(self) -> None:
        BlockMovementService.place(self.state, "b1", "c1", 50)

        self.assertEqual(["b1"], self.state.container_block_order["c1"])
        self.assertEqual("c1", self.state.block_locations["b1"])

    def test_move_block_between_containers(self) -> None:
        BlockMovementService.place(self.state, "b1", "c1", 0)
        BlockMovementService.place(self.state, "b2", "c1", 1)

        BlockMovementService.move(self.state, "b1", "c2", 0)

        self.assertEqual(["b2"], self.state.container_block_order["c1"])
        self.assertEqual(["b1"], self.state.container_block_order["c2"])
        self.assertEqual("c2", self.state.block_locations["b1"])

    def test_move_block_within_same_container_reorders_deterministically(self) -> None:
        BlockMovementService.place(self.state, "b1", "c1", 0)
        BlockMovementService.place(self.state, "b2", "c1", 1)

        BlockMovementService.move(self.state, "b1", "c1", 1)

        self.assertEqual(["b2", "b1"], self.state.container_block_order["c1"])

    def test_remove_block_cleans_state(self) -> None:
        BlockMovementService.place(self.state, "b1", "c1", 0)

        BlockMovementService.remove(self.state, "b1")

        self.assertNotIn("b1", self.state.blocks)
        self.assertNotIn("b1", self.state.block_locations)
        self.assertEqual([], self.state.container_block_order["c1"])


if __name__ == "__main__":
    unittest.main()
