from __future__ import annotations

from src.application.services.state import BlockFrameworkState
from src.domain.aggregates.container_aggregate import ContainerAggregate
from src.domain.block.models import Block
from src.domain.commands.models import (
    Command,
    CreateBlock,
    CreateContainer,
    MoveBlock,
    PlaceBlock,
    RemoveBlock,
    UpdateBlock,
)
from src.domain.container.models import Container
from src.domain.events.models import BlockCreated
from src.domain.operations.result import OperationResult
from src.domain.services.block_movement_service import BlockMovementService


class CommandHandler:
    def __init__(self, movement_service: BlockMovementService | None = None) -> None:
        self._movement_service = movement_service or BlockMovementService()

    def apply(self, state: BlockFrameworkState, command: Command) -> OperationResult:
        if isinstance(command, CreateContainer):
            return self._create_container(state, command)
        if isinstance(command, CreateBlock):
            return self._create_block(state, command)
        if isinstance(command, UpdateBlock):
            return self._update_block(state, command)
        if isinstance(command, PlaceBlock):
            return self._movement_service.place(state, command.block_id, command.container_id, command.position, command.metadata)
        if isinstance(command, MoveBlock):
            return self._movement_service.move(
                state,
                command.block_id,
                command.target_container_id,
                command.target_position,
                command.metadata,
            )
        if isinstance(command, RemoveBlock):
            return self._movement_service.remove(state, command.block_id, command.metadata)
        raise TypeError(f"Unsupported command type: {type(command)!r}")

    @staticmethod
    def _create_container(state: BlockFrameworkState, command: CreateContainer) -> OperationResult:
        if command.container_id in state.containers:
            return OperationResult.failed(command.metadata, [f"Container {command.container_id} already exists"])

        container = Container(
            container_id=command.container_id,
            container_type=command.container_type,
            metadata=dict(command.metadata_patch),
        )
        state.containers[command.container_id] = ContainerAggregate(container=container)
        state.increment_version()
        return OperationResult(
            success=True,
            metadata=command.metadata,
            affected_entities=[str(command.container_id)],
            version=state.version,
        )

    @staticmethod
    def _create_block(state: BlockFrameworkState, command: CreateBlock) -> OperationResult:
        if command.block_id in state.blocks:
            return OperationResult.failed(command.metadata, [f"Block {command.block_id} already exists"])

        state.blocks[command.block_id] = Block(
            block_id=command.block_id,
            block_type=command.block_type,
            payload=dict(command.payload),
            metadata=dict(command.metadata_patch),
        )
        state.increment_version()
        return OperationResult(
            success=True,
            metadata=command.metadata,
            events=[BlockCreated(metadata=command.metadata, block_id=command.block_id)],
            affected_entities=[str(command.block_id)],
            version=state.version,
        )

    @staticmethod
    def _update_block(state: BlockFrameworkState, command: UpdateBlock) -> OperationResult:
        block = state.blocks.get(command.block_id)
        if not block:
            return OperationResult.failed(command.metadata, [f"Block {command.block_id} does not exist"])

        block.metadata.update(command.metadata_patch)
        block.version += 1
        state.increment_version()
        return OperationResult(
            success=True,
            metadata=command.metadata,
            affected_entities=[str(command.block_id)],
            version=state.version,
        )
