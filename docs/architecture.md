# Block Engine Foundation Architecture

## Layering

- `src/domain/`
  - Pure domain models and movement logic.
  - No persistence or IO concerns.
- `src/application/`
  - Command orchestration over domain services.
  - Stateful snapshot model consumed by repositories.
- `src/infrastructure/`
  - Repository contracts and in-memory implementation.

## Command flow

1. Caller loads `BlockFrameworkState` from a repository.
2. Caller submits a command with operation metadata.
3. `CommandHandler` validates and applies behavior.
4. `BlockMovementService` performs deterministic ordering mutations.
5. Caller saves the updated snapshot.

## Determinism choices

- Ordering is integer index based.
- Placement/move indexes are bounded into valid list ranges.
- Container block order and block location mappings are updated together.

## Extension points

- Replace in-memory repository with persistent implementations.
- Add read models and query services in application layer.
- Expand command set (resize, split, merge, conflict resolution) without coupling to a specific product domain.
