export interface BlockShape {
  id: string;
  state: string;
  extent: BlockExtent | number | RawExtent;
  payload?: Record<string, unknown>;
  startTime?: number;
}

export interface RawExtent {
  value?: number;
  unit?: string;
  extent_type?: string;
  extentType?: string;
}

export class BlockExtent {
  public readonly value: number;
  public readonly unit: string;
  public readonly extentType: string;

  constructor(value: number, unit = "units", extentType = "generic") {
    if (value <= 0) {
      throw new Error("BlockExtent value must be positive");
    }
    if (!unit.trim()) {
      throw new Error("BlockExtent unit cannot be empty");
    }
    if (!extentType.trim()) {
      throw new Error("BlockExtent extentType cannot be empty");
    }

    this.value = value;
    this.unit = unit;
    this.extentType = extentType;
  }
}

export class BlockState {
  public readonly value: string;

  constructor(value: string) {
    if (!value.trim()) {
      throw new Error("BlockState value cannot be empty");
    }
    this.value = value;
  }

  public toString(): string {
    return this.value;
  }
}

export class Block {
  public id: string;
  public state: string;
  public extent: BlockExtent;
  public payload: Record<string, unknown>;
  public startTime: number;

  constructor({ id, state, extent, payload = {}, startTime = 0 }: BlockShape) {
    if (!id.trim()) {
      throw new Error("Block id cannot be empty");
    }
    if (!state.trim()) {
      throw new Error("Block state cannot be empty");
    }

    this.id = id;
    this.state = state;
    this.extent = normalizeBlockExtent({ extent });
    this.payload = { ...payload };
    this.startTime = startTime;
  }
}

function createBlockId(): string {
  return `block-${Date.now()}-${Math.random().toString(16).slice(2, 10)}`;
}

export interface PlacementSnapshot {
  blockId: string;
  placement: number;
  extent: number;
}

export function normalizeBlockExtent(block: { extent?: unknown }, defaultValue = 1): BlockExtent {
  const rawExtent = block.extent;

  if (rawExtent instanceof BlockExtent) {
    return rawExtent;
  }

  if (rawExtent === undefined || rawExtent === null) {
    return new BlockExtent(defaultValue);
  }

  if (typeof rawExtent === "number" && rawExtent > 0) {
    return new BlockExtent(rawExtent);
  }

  if (typeof rawExtent === "object") {
    const typedExtent = rawExtent as RawExtent;
    const value = typedExtent.value ?? defaultValue;
    const unit = typedExtent.unit ?? "units";
    const extentType = typedExtent.extent_type ?? typedExtent.extentType ?? "generic";

    try {
      return new BlockExtent(Number(value), String(unit), String(extentType));
    } catch {
      return new BlockExtent(defaultValue);
    }
  }

  return new BlockExtent(defaultValue);
}

export function instantiateBlockFromSource(sourceBlock: Block): Block {
  const canonicalExtent = normalizeBlockExtent(sourceBlock);

  return new Block({
    id: createBlockId(),
    state: sourceBlock.state,
    extent: canonicalExtent,
    payload: JSON.parse(JSON.stringify(sourceBlock.payload)),
    startTime: sourceBlock.startTime
  });
}

export function resizePlacement({
  start,
  extent,
  delta,
  direction
}: {
  start: number;
  extent: number;
  delta: number;
  direction: "forward" | "backward";
}): { start: number; extent: number } {
  if (extent <= 0) {
    throw new Error("extent must be positive");
  }

  const next =
    direction === "forward"
      ? { start, extent: extent + delta }
      : { start: start + delta, extent: extent - delta };

  if (next.extent <= 0) {
    throw new Error("resize operation produced non-positive extent");
  }

  return next;
}

export function createPlacementSnapshot(block: Block): PlacementSnapshot {
  return {
    blockId: block.id,
    placement: block.startTime,
    extent: block.extent.value
  };
}

export function changeBlockState(block: Block, newState: string): Block {
  if (!newState.trim()) {
    throw new Error("newState cannot be empty");
  }

  block.state = newState;
  return block;
}

export function changeBlockExtent(block: Block, newExtent: BlockExtent | number | RawExtent): Block {
  block.extent = newExtent instanceof BlockExtent ? newExtent : normalizeBlockExtent({ extent: newExtent });
  return block;
}

// snake_case aliases for compatibility with existing language-agnostic naming.
export const normalize_block_extent = normalizeBlockExtent;
export const instantiate_block_from_source = instantiateBlockFromSource;
export const resize_placement = resizePlacement;
export const create_placement_snapshot = createPlacementSnapshot;
export const change_block_state = changeBlockState;
export const change_block_extent = changeBlockExtent;
