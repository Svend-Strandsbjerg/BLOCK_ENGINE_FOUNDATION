from __future__ import annotations

from .block import Block
from .block_extent import BlockExtent, normalize_block_extent


def change_block_state(block: Block, new_state: str) -> Block:
    """Return block with updated opaque state."""

    if not new_state.strip():
        raise ValueError("new_state cannot be empty")
    block.state = new_state
    return block


def change_block_extent(block: Block, new_extent: BlockExtent | float | dict[str, object]) -> Block:
    """Return block with updated canonical extent."""

    if isinstance(new_extent, BlockExtent):
        block.extent = new_extent
        return block

    class _ExtentCarrier:
        extent = new_extent

    block.extent = normalize_block_extent(_ExtentCarrier())
    return block
