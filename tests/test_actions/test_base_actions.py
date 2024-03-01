from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from meldingen_core.actions.base import (
    BaseCreateAction,
    BaseDeleteAction,
    BaseListAction,
    BaseRetrieveAction,
    BaseUpdateAction,
)
from meldingen_core.exceptions import NotFoundException
from meldingen_core.repositories import BaseRepository


class DummyModel:
    name: str | None


@pytest.fixture
def base_list_action() -> BaseListAction[DummyModel, DummyModel]:
    return BaseListAction(Mock(BaseRepository))


@pytest.mark.asyncio
async def test_base_create_action(mocker: MockerFixture) -> None:
    action: BaseCreateAction[DummyModel, DummyModel] = BaseCreateAction(Mock(BaseRepository))

    spy = mocker.spy(action._repository, "save")

    dummy = DummyModel()

    await action(dummy)

    spy.assert_called_once_with(dummy)


@pytest.mark.asyncio
async def test_base_list_action(
    base_list_action: BaseListAction[DummyModel, DummyModel],
    mocker: MockerFixture,
) -> None:
    spy = mocker.spy(base_list_action._repository, "list")

    await base_list_action()

    spy.assert_called_once()


@pytest.mark.parametrize(
    "limit",
    [1, 5, 10, 20],
)
@pytest.mark.asyncio
async def test_base_list_action_limit(
    base_list_action: BaseListAction[DummyModel, DummyModel], limit: int, mocker: MockerFixture
) -> None:
    spy = mocker.spy(base_list_action._repository, "list")

    await base_list_action(limit=limit)

    spy.assert_called_once_with(limit=limit, offset=None)


@pytest.mark.parametrize("offset", [1, 5, 10, 20])
@pytest.mark.asyncio
async def test_base_list_action_offset(
    base_list_action: BaseListAction[DummyModel, DummyModel],
    offset: int,
    mocker: MockerFixture,
) -> None:
    spy = mocker.spy(base_list_action._repository, "list")

    await base_list_action(offset=offset)

    spy.assert_called_once_with(limit=None, offset=offset)


@pytest.mark.parametrize(
    "limit, offset",
    [(10, 0), (5, 0), (10, 10), (20, 0)],
)
@pytest.mark.asyncio
async def test_base_list_action_limit_offset(
    base_list_action: BaseListAction[DummyModel, DummyModel],
    limit: int,
    offset: int,
    mocker: MockerFixture,
) -> None:
    spy = mocker.spy(base_list_action._repository, "list")

    await base_list_action(limit=limit, offset=offset)

    spy.assert_called_once_with(limit=limit, offset=offset)


@pytest.mark.parametrize("pk", [1, 2, 3, 4, 5])
@pytest.mark.asyncio
async def test_base_retrieve_action(pk: int, mocker: MockerFixture) -> None:
    action: BaseRetrieveAction[DummyModel, DummyModel] = BaseRetrieveAction(Mock(BaseRepository))

    spy = mocker.spy(action._repository, "retrieve")

    await action(pk=pk)

    spy.assert_called_once_with(pk=pk)


@pytest.mark.parametrize("pk", [1, 2, 3, 4, 5])
@pytest.mark.asyncio
async def test_base_delete_action(pk: int, mocker: MockerFixture) -> None:
    action: BaseDeleteAction[DummyModel, DummyModel] = BaseDeleteAction(Mock(BaseRepository))

    spy = mocker.spy(action._repository, "delete")

    await action(pk=pk)

    spy.assert_called_once_with(pk=pk)


@pytest.mark.asyncio
async def test_base_update_action(mocker: MockerFixture) -> None:
    action: BaseUpdateAction[DummyModel, DummyModel] = BaseUpdateAction(Mock(BaseRepository))

    spy = mocker.spy(action._repository, "save")

    dummy = DummyModel()

    mocker.patch.object(action._repository, "retrieve", return_value=dummy)

    await action(101, {"name": "new name"})

    spy.assert_called_once_with(dummy)
    assert dummy.name == "new name"


@pytest.mark.asyncio
async def test_base_delete_action_not_found(mocker: MockerFixture) -> None:
    action: BaseUpdateAction[DummyModel, DummyModel] = BaseUpdateAction(Mock(BaseRepository))

    mocker.patch.object(action._repository, "retrieve", return_value=None)
    with pytest.raises(NotFoundException) as exc_info:
        await action(101, {"name": "new name"})
