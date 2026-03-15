# Block Engine Architecture (v1)

## Layered structure

- **Domain (`src/domain`)**
  - Blocks, containers, aggregates, policies, domain events, operation outcomes
  - Positioning contracts (`PositionStrategy`) and sequence implementation (`SequencePositionStrategy`)
- **Application (`src/application`)**
  - Command orchestration (`CommandHandler`)
  - Query/read service (`FrameworkQueryService`)
  - Mapping boundary for external contracts (`DomainReadModelMapper`, `OperationResultMapper`)
- **Infrastructure (`src/infrastructure`)**
  - Snapshot repository abstraction
  - Version-aware in-memory implementation with optimistic concurrency checks

## Aggregate and orchestration boundaries

- `ContainerAggregate` owns only ordering/state consistency for its container.
- Cross-container move orchestration and policy coordination are handled by `BlockMovementService`.
- `CommandHandler` remains application-level dispatch and transaction-style coordination.

## Deterministic positioning and reads

- Container ordering is strategy-based, not hardcoded to one concrete class.
- Current deterministic strategy is sequence ordering with normalized indexes.
- Query layer always returns container blocks in deterministic order to support stable client rendering.

## Rejection and validation model

- Policy and validation failures are represented by `OperationRejection`:
  - `code`
  - `message`
  - `entity_ids`
  - optional `context`
- `OperationResult` includes structured rejections plus synchronization deltas.

## Deterministic client synchronization support

For every successful operation, consumers can deterministically identify:

- which blocks changed (`affected_block_ids`)
- which containers changed (`affected_container_ids`)
- how locations changed (`location_changes`)
- the current framework version (`version`)

This allows efficient partial redraw/update logic in future UI/API adapters.

## Extensibility without overengineering

The architecture intentionally keeps extension points small:

- Add new `PositionStrategy` implementations for time/grid/span models.
- Add/replace policies for domain-specific constraints.
- Add adapter-specific serializers/controllers outside the core while reusing read models and mappers.
- Swap repository backend without changing domain/application contracts.
