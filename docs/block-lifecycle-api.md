# Block Engine Runtime API

`BLOCK_ENGINE_FOUNDATION` exposes a runtime-importable Python package: `block_engine_foundation`.

## Canonical model

```python
from block_engine_foundation import Block, BlockExtent, BlockState

block = Block(
    id="block-1",
    state="draft",
    extent=BlockExtent(value=30, unit="minutes", extent_type="time"),
    payload={"source": "pattern-psp"},
    start_time=540,
)
```

- `state` is an opaque marker string; applications define semantics.
- `extent` is a generic measurable value.
- `payload` is arbitrary metadata.

## Exported capabilities

### `normalizeBlockExtent(block)`

Returns canonical extent data and applies safe defaults when extent is missing or invalid.

### `instantiateBlockFromSource(source_block)`

Creates a new block from any source block:

- clones payload metadata
- normalizes extent
- generates a new block id
- preserves source state (application may change it afterwards)

### `resizePlacement(start, extent, delta, direction)`

Deterministic geometric resize helper.

- `direction="forward"`: start fixed, extent adjusted by `delta`.
- `direction="backward"`: trailing edge fixed via start shift and extent adjustment.
- rejects non-positive resulting extent.

Returns:

```python
{"start": float, "extent": float}
```

### `createPlacementSnapshot(block)`

Captures deterministic placement baseline:

```python
PlacementSnapshot(blockId, placement, extent)
```

### `changeBlockState(block, new_state)`

Updates `Block.state` as an opaque lifecycle marker.

### `changeBlockExtent(block, new_extent)`

Updates `Block.extent` using canonical normalization.

## Example import surface

```python
from block_engine_foundation import (
    Block,
    BlockState,
    BlockExtent,
    normalizeBlockExtent,
    instantiateBlockFromSource,
    resizePlacement,
    createPlacementSnapshot,
    changeBlockState,
    changeBlockExtent,
)
```
