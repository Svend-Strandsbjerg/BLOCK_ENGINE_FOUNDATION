from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class BlockView:
    block_id: str
    block_type: str
    metadata: dict[str, object] = field(default_factory=dict)
    payload: dict[str, object] = field(default_factory=dict)
    version: int = 0


@dataclass(frozen=True, slots=True)
class ContainerBlockView:
    block_id: str
    order_index: int


@dataclass(frozen=True, slots=True)
class ContainerSnapshotView:
    container_id: str
    container_type: str
    strategy: str
    version: int
    blocks: list[ContainerBlockView] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class BlockLocationView:
    block_id: str
    container_id: str | None


@dataclass(frozen=True, slots=True)
class FrameworkVersionView:
    version: int
