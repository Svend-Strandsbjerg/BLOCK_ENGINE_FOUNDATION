# Foundation Concept: Abstract Block Movement Engine

This foundation provides a reusable, domain-agnostic block movement engine focused on deterministic behavior, explicit contracts, and enterprise-ready extension points.

## Core abstractions

- **Value objects**
  - `BlockId`, `ContainerId`, `OperationId`
  - `SequencePosition` as the first `Position` strategy implementation
  - `OperationMetadata` for traceability and idempotency context
- **Entities / aggregates**
  - `Block` as a movable domain unit
  - `ContainerAggregate` as the consistency boundary for ordered placement
- **Policies**
  - `PlacementPolicy`
  - `MovementPolicy`
  - `PositionConflictPolicy`
  - `ContainerConstraintPolicy`
- **Operation outcome model**
  - `OperationResult` returns success/failure, violations, emitted events, affected entities, and versions.
- **Domain events**
  - `BlockCreated`, `BlockPlaced`, `BlockMoved`, `BlockRemoved`, `BlockReordered`

## Aggregate boundaries and state

The engine snapshot (`BlockFrameworkState`) keeps:

- block registry
- container aggregates
- block-to-container location index
- snapshot version

Containers are treated as stronger boundaries for block ordering consistency. Cross-container movement is orchestrated by the application layer/service.

## Deterministic command flow

1. A command with `OperationMetadata` enters `CommandHandler`.
2. Handler orchestrates create/update actions directly and delegates movement operations to `BlockMovementService`.
3. Movement service evaluates policies.
4. If valid, container aggregate ordering is updated deterministically.
5. `OperationResult` and domain events are returned for tracing and integrations.

## Persistence and concurrency readiness

Repository contract is snapshot-oriented and version-aware:

- `load_snapshot()` returns `PersistedSnapshot`
- `save_snapshot(state, expected_version=...)` supports optimistic concurrency checks

In-memory implementation is intentionally simple but compatible with future database/event-backed implementations.

## Extension points

- Replace policies for new domain rules without rewriting movement orchestration.
- Add new `Position` strategy variants (time-range, coordinates, span/quantity) while preserving command and result contracts.
- Add projection/read-model layers from emitted domain events.
