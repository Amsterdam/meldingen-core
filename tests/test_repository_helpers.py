from typing import cast
from unittest.mock import AsyncMock

import pytest

from meldingen_core.exceptions import NotFoundException
from meldingen_core.repositories import BaseRepository
from meldingen_core.repository_helpers import retrieve_or_raise_not_found


class TestRetrieveOrRaiseNotFound:
    @pytest.mark.anyio
    async def test_returns_item_when_found(self) -> None:
        repository = AsyncMock(spec=BaseRepository)
        repository.retrieve = AsyncMock(return_value="item")

        result = await retrieve_or_raise_not_found(repository, 123)

        assert result == "item"
        repository.retrieve.assert_awaited_once_with(123)

    @pytest.mark.anyio
    async def test_raises_not_found_with_default_message(self) -> None:
        class SomeEntityRepository:
            async def retrieve(self, id: int):
                return None

        repository = SomeEntityRepository()

        with pytest.raises(NotFoundException) as exception_info:
            await retrieve_or_raise_not_found(cast(BaseRepository, repository), 456)

        assert str(exception_info.value) == "SomeEntityRepository item not found"

    @pytest.mark.anyio
    async def test_raises_not_found_with_custom_message(self) -> None:
        repository = AsyncMock(spec=BaseRepository)
        repository.retrieve = AsyncMock(return_value=None)

        with pytest.raises(NotFoundException) as exception_info:
            await retrieve_or_raise_not_found(repository, 789, "Custom not found message")

        assert str(exception_info.value) == "Custom not found message"
        repository.retrieve.assert_awaited_once_with(789)
