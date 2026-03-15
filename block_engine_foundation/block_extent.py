from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BlockExtent:
    """Canonical measurable extent for a block."""

    value: float
    unit: str = "units"
    extent_type: str = "generic"

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("BlockExtent value must be positive")
        if not self.unit.strip():
            raise ValueError("BlockExtent unit cannot be empty")
        if not self.extent_type.strip():
            raise ValueError("BlockExtent extent_type cannot be empty")


def normalize_block_extent(block: object, default_value: float = 1) -> BlockExtent:
    """Return a canonical extent for any block-like source."""

    raw_extent = getattr(block, "extent", None)
    if isinstance(raw_extent, BlockExtent):
        return raw_extent

    if raw_extent is None:
        return BlockExtent(value=default_value)

    if isinstance(raw_extent, (int, float)) and raw_extent > 0:
        return BlockExtent(value=float(raw_extent))

    if isinstance(raw_extent, dict):
        value = raw_extent.get("value", default_value)
        unit = raw_extent.get("unit", "units")
        extent_type = raw_extent.get("extent_type", raw_extent.get("extentType", "generic"))
        try:
            return BlockExtent(value=float(value), unit=str(unit), extent_type=str(extent_type))
        except (TypeError, ValueError):
            return BlockExtent(value=default_value)

    return BlockExtent(value=default_value)
