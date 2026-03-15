# Block Engine Architecture

## Layered structure

- **Domain (`src/domain`)**
  - Value objects, entities, aggregates, policies, domain events, and operation results.
  - Deterministic movement orchestration in `BlockMovementService`.
- **Application (`src/application`)**
  - Command handler orchestrates command execution against snapshot state.
  - Coordinates cross-aggregate movement through domain service.
- **Infrastructure (`src/infrastructure`)**
  - Repository abstractions and concrete persistence adapters.
  - Current implementation: version-aware in-memory snapshot repository.

## Design decisions

### 1) Explicit value objects over primitives

Core identifiers and operation metadata are first-class value objects to improve type safety, readability, and contract clarity.

### 2) Positioning abstraction

`Position` is strategy-oriented and currently implemented as `SequencePosition`. This keeps deterministic ordering today while allowing future position models.

### 3) Policy-driven domain rules

Placement and movement decisions are delegated to policy interfaces. `BlockMovementService` orchestrates flow and state transitions rather than hard-coding business decisions.

### 4) Structured operation outcomes

All commands return `OperationResult` with:

- success/failure
- violations
- emitted events
- affected entities
- snapshot version

This improves observability, testability, and future integrations.

### 5) Domain event model

State transitions emit domain events (`BlockCreated`, `BlockPlaced`, `BlockMoved`, `BlockRemoved`, `BlockReordered`) to support auditability and projection pipelines.

### 6) Aggregate boundaries

Container ordering behavior is contained in `ContainerAggregate`. The global snapshot remains deterministic but is no longer modeled as one mutable ordering object.

### 7) Version and concurrency readiness

State and repository contracts include versions and expected-version checks, enabling optimistic concurrency evolution without redesign.

## Command lifecycle

1. Command is validated by type in `CommandHandler`.
2. Domain action executes.
3. Policies evaluate movement/placement constraints when relevant.
4. State updates occur deterministically.
5. Domain events are emitted.
6. `OperationResult` is returned to caller.

## Future evolution

- Introduce richer policy sets per implementation domain.
- Add read-model/projector pipeline from domain events.
- Add persistent aggregate repositories and snapshot/event hybrid stores.
- Extend position strategy library without altering command orchestration contracts.
