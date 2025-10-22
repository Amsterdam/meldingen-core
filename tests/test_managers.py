from unittest.mock import AsyncMock, Mock

import pytest

from meldingen_core.managers import RelationshipManager
from meldingen_core.repositories import BaseRepository


class DummyParent: ...


class DummyRelated: ...

class TestRelationshipManager:

    def test_can_instantiate_relationship_manager(self) -> None:
        repository = Mock()
        get_related = AsyncMock()
        manager = RelationshipManager(repository, get_related)

        assert isinstance(manager, RelationshipManager)
        assert manager._get_related == get_related
        assert manager._repository == repository

    @pytest.mark.anyio
    async def adds_relationship_when_not_existing(self) -> None:
        repository = Mock()
        repository.save = AsyncMock()
        get_related = AsyncMock(return_value=[])
        manager = RelationshipManager(repository, get_related)

        assert isinstance(manager, RelationshipManager)
        assert manager._get_related == get_related
        assert manager._repository == repository

        parent = DummyParent()
        related = DummyRelated()

        await manager.add_relationship(parent, related)

        get_related.assert_called_once_with(parent)
        manager._get_related.assert_awaited_once_with(parent)
        manager._repository.save.assert_awaited_once_with(parent)

        repository.save.assert_awaited_once_with(parent)


    @pytest.mark.anyio
    async def does_not_add_relationship_when_already_exists(self) -> None:
        class ParentDummyRelationshipManager(RelationshipManager[DummyParent, DummyRelated]): ...


        repository = Mock()
        repository.save = AsyncMock()
        related_item = DummyRelated()
        get_related = AsyncMock(return_value=[related_item])
        manager: ParentDummyRelationshipManager[DummyParent, DummyRelated] = ParentDummyRelationshipManager(repository=repository, get_related=get_related)
        assert isinstance(manager, ParentDummyRelationshipManager)

        parent = DummyParent()

        await manager.add_relationship(parent, related_item)

        get_related.assert_called_once_with(parent)
        repository.save.assert_not_awaited()


    @pytest.mark.anyio
    async def retrieves_related_items(self) -> None:
        class ParentDummyRelationshipManager(RelationshipManager[DummyParent, DummyRelated]): ...

        parent = DummyParent()
        related_items = [DummyRelated(), DummyRelated()]
        get_related = AsyncMock(return_value=related_items)
        repository = Mock(BaseRepository)
        manager: ParentDummyRelationshipManager[DummyParent, DummyRelated] = ParentDummyRelationshipManager(repository, get_related)

        result = await manager.get_related(parent)

        get_related.assert_called_once_with(parent)
        assert result == related_items
