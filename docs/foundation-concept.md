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
