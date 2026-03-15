from .block import Block
from .block_extent import BlockExtent, normalize_block_extent
from .block_factories import (
    PlacementSnapshot,
    create_placement_snapshot,
    instantiate_block_from_source,
)
from .block_resize import resize_placement
from .block_state import BlockState
from .lifecycle import change_block_extent, change_block_state

# camelCase runtime exports
normalizeBlockExtent = normalize_block_extent
instantiateBlockFromSource = instantiate_block_from_source
resizePlacement = resize_placement
createPlacementSnapshot = create_placement_snapshot
changeBlockState = change_block_state
changeBlockExtent = change_block_extent

__all__ = [
    "Block",
    "BlockState",
    "BlockExtent",
    "PlacementSnapshot",
    "normalize_block_extent",
    "instantiate_block_from_source",
    "resize_placement",
    "create_placement_snapshot",
    "change_block_state",
    "change_block_extent",
    "normalizeBlockExtent",
    "instantiateBlockFromSource",
    "resizePlacement",
    "createPlacementSnapshot",
    "changeBlockState",
    "changeBlockExtent",
]
