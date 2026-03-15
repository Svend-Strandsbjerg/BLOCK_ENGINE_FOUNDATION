# Foundation Concept: Abstract Block Engine (v1)

This repository now provides a lightweight, domain-agnostic block engine that is deterministic, policy-driven, and ready for UI integrations through read models.

## Core domain model

- **Value objects**
  - `BlockId`, `ContainerId`, `OperationId`
  - `Position` protocol with `SequencePosition` as the initial implementation
  - `OperationMetadata` for traceability/idempotency context
- **Entities / aggregates**
  - `Block` as a domain-neutral movable unit
  - `ContainerAggregate` as the ordering consistency boundary
- **Positioning strategy abstraction**
  - `PositionStrategy` contract decouples aggregate behavior from one concrete position model
  - `SequencePositionStrategy` is the initial deterministic implementation
  - Future strategy families can be added without redesigning command orchestration

## Policy-driven orchestration

- Command orchestration stays in `CommandHandler` and `BlockMovementService`
- Rule decisions are delegated to policies:
  - `PlacementPolicy`
  - `MovementPolicy`
  - `PositionConflictPolicy`
  - `ContainerConstraintPolicy`
- Aggregates remain lean and focused on state consistency (position updates + version updates)

## Operation outcome and rejection model

`OperationResult` is structured for domain and client synchronization use:

- success/failure
- emitted events
- structured rejections (`OperationRejection`) with code/message/entity/context
- affected block ids
- affected container ids
- location change deltas (previous/current container)
- updated framework version

This supports deterministic client refresh patterns without introducing UI logic into the domain.

## Read/query model for UI readiness

A lightweight read layer is provided without full CQRS ceremony:

- `FrameworkQueryService` exposes common deterministic reads:
  - container snapshot (stable display order)
  - block location
  - blocks for a container
  - framework version
  - operation update payload for client sync
- Read models are explicit (`ContainerSnapshotView`, `BlockView`, `BlockLocationView`, `FrameworkVersionView`)

## Mapping boundary for external consumers

A dedicated mapping boundary keeps internal domain models private:

- `DomainReadModelMapper` maps state/aggregates to read models
- `OperationResultMapper` maps operation outcomes to external-safe payloads

This prevents leaking raw domain internals to APIs/UIs and keeps adapter evolution clean.

## Scope and non-goals

- No swimlane/timesheet/product-specific rules in core
- No frontend code or framework dependencies
- No heavy framework ceremony; only minimal abstractions required for extension and deterministic behavior


## Abstract block state support

The foundation now treats block state as a first-class domain concept:

- `Block` includes an optional `BlockState` value object with a generic string `code`.
- State values are not enumerated in the foundation; consuming solutions define meaningful codes (for example, `planned` or `approved`).
- `ChangeBlockState` provides explicit state change commands via the existing command/handler flow.
- `BlockStateChanged` events emit both `previous_state` and `current_state` for traceability and downstream adapters.
- Read models expose state through `BlockView.state` for API/UI filtering, grouping, and presentation mapping.
- Optional transition validation is available through `StateTransitionPolicy`; the default implementation allows all transitions.

This keeps workflow rules and visual semantics outside the core framework while preserving a reusable state mechanism.


## Abstract block extent support

The foundation now supports a generic measurable extent for each block, without assuming product semantics:

- `BlockExtent` carries:
  - required numeric `value`
  - optional `unit` (for example `minutes`, `pieces`, `hours`)
  - optional `extent_type` (for example `time`, `quantity`, `capacity`)
- `Block.extent` stores the current abstract measure.
- `ChangeBlockExtent` allows applications to request extent updates through the standard command pipeline.
- `BlockExtentChanged` events emit `previous_extent` and `current_extent` alongside operation metadata for traceability.
- Query/read models expose extent through `BlockView.extent` so consumers can render or synchronize client state.
- Optional validation is available through `BlockExtentPolicy`; default behavior remains permissive.

### UI interaction boundary

This capability intentionally models **domain measure updates**, not interaction mechanics.

The core framework does **not** include concepts such as drag handles, edge dragging, snapping, pixels, or gesture semantics. A UI computes the target extent value and submits it as a normal command.

Example flow:

1. User resizes a visual block in a client.
2. Client calculates a new abstract extent (for example `value=90`, `unit=minutes`).
3. Client sends `ChangeBlockExtent`.
4. Framework validates via policies, updates state, emits `BlockExtentChanged`, and returns an operation result.
5. Client refreshes from read models and re-renders according to its own visual logic.
