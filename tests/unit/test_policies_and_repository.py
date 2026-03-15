import unittest

from src.application.services.state import BlockFrameworkState
from src.domain.aggregates.container_aggregate import ContainerAggregate
from src.domain.block.models import Block, BlockExtent
from src.domain.common.value_objects import (
    BlockId,
    ContainerId,
    OperationId,
    OperationMetadata,
    SequencePosition,
)
from src.domain.container.models import Container
from src.domain.operations.rejection import OperationRejection
from src.domain.policies.movement_policies import PlacementPolicy
from src.domain.services.block_movement_service import BlockMovementService
from src.infrastructure.repositories.in_memory import InMemoryStateRepository


class RejectAllPlacementPolicy(PlacementPolicy):
    def validate(self, state, block_id, container_id, position):
        return [
            OperationRejection(
                code="placement.blocked",
                message="placement blocked by policy",
                entity_ids=[str(block_id), str(container_id)],
            )
        ]


class PolicyAndRepositoryTests(unittest.TestCase):
    def test_policy_can_reject_placement(self) -> None:
        state = BlockFrameworkState(
            blocks={BlockId("b1"): Block(block_id=BlockId("b1"), block_type="generic")},
            containers={
                ContainerId("c1"): ContainerAggregate(
                    container=Container(container_id=ContainerId("c1"), container_type="generic")
                )
            },
        )
        service = BlockMovementService(placement_policy=RejectAllPlacementPolicy())

        result = service.place(
            state,
            BlockId("b1"),
            ContainerId("c1"),
            SequencePosition(order_index=0),
            OperationMetadata(operation_id=OperationId("op-1")),
        )

        self.assertFalse(result.success)
        self.assertEqual("placement.blocked", result.rejections[0].code)
        self.assertIn("placement blocked by policy", result.violations)


    def test_block_extent_value_object_rejects_blank_descriptors(self) -> None:
        with self.assertRaises(ValueError):
            BlockExtent(value=1, unit="   ")

        with self.assertRaises(ValueError):
            BlockExtent(value=1, extent_type="   ")

    def test_repository_expected_version_check(self) -> None:
        repository = InMemoryStateRepository()
        snapshot = repository.load_snapshot()
        state = snapshot.state
        state.increment_version()
        repository.save_snapshot(state, expected_version=0)

        with self.assertRaises(ValueError):
            repository.save_snapshot(state, expected_version=0)


if __name__ == "__main__":
    unittest.main()
