from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from uuid import uuid4

from .block import Block
from .block_extent import BlockExtent, normalize_block_extent


@dataclass(frozen=True, slots=True)
class PlacementSnapshot:
    blockId: str
    placement: float
    extent: float


def instantiate_block_from_source(source_block: Block) -> Block:
    """Create a new block instance by cloning a source block."""

    canonical_extent: BlockExtent = normalize_block_extent(source_block)
    return Block(
        id=str(uuid4()),
        state=source_block.state,
        extent=canonical_extent,
        payload=deepcopy(source_block.payload),
        start_time=source_block.start_time,
    )


def create_placement_snapshot(block: Block) -> PlacementSnapshot:
    """Capture a deterministic block placement snapshot."""

    return PlacementSnapshot(
        blockId=block.id,
        placement=block.start_time,
        extent=block.extent.value,
    )
