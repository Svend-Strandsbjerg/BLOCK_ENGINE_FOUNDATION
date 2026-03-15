# Foundation Concept: Abstract Block Movement

This repository now includes a minimal, domain-agnostic framework for managing movable blocks inside ordered containers.

## Core abstractions

- **Block**: Generic unit of information with flexible metadata and payload.
- **Container**: Ordered context where blocks are placed.
- **Position**: Deterministic index-based ordering model.

## Deterministic state model

State is represented by `BlockFrameworkState`:

- `blocks`: all known blocks keyed by ID.
- `containers`: all known containers keyed by ID.
- `container_block_order`: deterministic ordering of block IDs per container.
- `block_locations`: reverse lookup of where each block is currently placed.

Operations are applied as explicit commands through the command handler.

## Traceability

Every command carries `OperationMetadata`:

- `operation_id`
- `timestamp`
- `source`
- `user_or_system`

This supports auditability and future event-oriented expansion.

## Scope of this implementation

Included:

- Core domain models
- Command model
- Movement service for placement/reordering/relocation/removal
- In-memory repository abstraction
- Unit tests for movement and command handling

Not included:

- UI
- Domain-specific business logic
- Persistence backends beyond in-memory
- Distributed/event-sourcing infrastructure
