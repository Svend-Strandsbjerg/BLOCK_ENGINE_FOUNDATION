import unittest

from block_engine_foundation import (
    Block,
    BlockExtent,
    changeBlockExtent,
    changeBlockState,
    createPlacementSnapshot,
    instantiateBlockFromSource,
    normalizeBlockExtent,
    resizePlacement,
)


class BlockLifecycleApiTests(unittest.TestCase):
    def test_normalize_block_extent_preserves_valid_or_defaults_invalid(self) -> None:
        source = Block(id="src-1", state="draft", extent=BlockExtent(15), payload={})
        self.assertEqual(15, normalizeBlockExtent(source).value)

        source.extent = {"value": -1}
        self.assertEqual(1, normalizeBlockExtent(source).value)

    def test_instantiate_block_from_source_clones_payload_and_generates_id(self) -> None:
        source = Block(
            id="src-2",
            state="draft",
            extent=BlockExtent(30),
            payload={"kind": "psp", "nested": {"a": 1}},
            start_time=120,
        )

        instantiated = instantiateBlockFromSource(source)

        self.assertEqual("draft", instantiated.state)
        self.assertNotEqual(source.id, instantiated.id)
        self.assertEqual(30, instantiated.extent.value)
        self.assertEqual(source.payload, instantiated.payload)
        self.assertIsNot(source.payload["nested"], instantiated.payload["nested"])

    def test_resize_placement_forward_and_backward(self) -> None:
        forward = resizePlacement(start=100, extent=6, delta=2, direction="forward")
        self.assertEqual({"start": 100, "extent": 8}, forward)

        backward = resizePlacement(start=100, extent=6, delta=2, direction="backward")
        self.assertEqual({"start": 102, "extent": 4}, backward)

    def test_create_placement_snapshot(self) -> None:
        block = Block(id="b-1", state="stable", extent=BlockExtent(30), payload={}, start_time=480)

        snapshot = createPlacementSnapshot(block)

        self.assertEqual("b-1", snapshot.blockId)
        self.assertEqual(480, snapshot.placement)
        self.assertEqual(30, snapshot.extent)

    def test_change_block_state_and_extent(self) -> None:
        block = Block(id="b-2", state="draft", extent=BlockExtent(10), payload={})

        changeBlockState(block, "published")
        changeBlockExtent(block, {"value": 12, "unit": "minutes", "extent_type": "time"})

        self.assertEqual("published", block.state)
        self.assertEqual(12, block.extent.value)


if __name__ == "__main__":
    unittest.main()
