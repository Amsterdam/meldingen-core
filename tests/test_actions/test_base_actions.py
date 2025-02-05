from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from meldingen_core import SortingDirection
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
def base_list_action() -> BaseListAction[DummyModel]:
    return BaseListAction(Mock(BaseRepository))


@pytest.mark.anyio
async def test_base_create_action(mocker: MockerFixture) -> None:
    action: BaseCreateAction[DummyModel] = BaseCreateAction(Mock(BaseRepository))

    spy = mocker.spy(action._repository, "save")

    dummy = DummyModel()

    await action(dummy)

    spy.assert_called_once_with(dummy)


@pytest.mark.anyio
async def test_base_list_action(
    base_list_action: BaseListAction[DummyModel],
    mocker: MockerFixture,
) -> None:
    spy = mocker.spy(base_list_action._repository, "list")

    await base_list_action()

    spy.assert_called_once()


@pytest.mark.parametrize(
    "limit",
    [1, 5, 10, 20],
)
@pytest.mark.anyio
async def test_base_list_action_limit(
    base_list_action: BaseListAction[DummyModel], limit: int, mocker: MockerFixture
) -> None:
    spy = mocker.spy(base_list_action._repository, "list")

    await base_list_action(limit=limit)

    spy.assert_called_once_with(limit=limit, offset=None, sort_attribute_name=None, sort_direction=None)


@pytest.mark.parametrize("offset", [1, 5, 10, 20])
@pytest.mark.anyio
async def test_base_list_action_offset(
    base_list_action: BaseListAction[DummyModel],
    offset: int,
    mocker: MockerFixture,
) -> None:
    spy = mocker.spy(base_list_action._repository, "list")

    await base_list_action(offset=offset)

    spy.assert_called_once_with(limit=None, offset=offset, sort_attribute_name=None, sort_direction=None)


@pytest.mark.anyio
async def test_base_list_action_sort_attribute_name(
    base_list_action: BaseListAction[DummyModel],
    mocker: MockerFixture,
) -> None:
    spy = mocker.spy(base_list_action._repository, "list")

    await base_list_action(sort_attribute_name="name")

    spy.assert_called_once_with(limit=None, offset=None, sort_attribute_name="name", sort_direction=None)


@pytest.mark.parametrize("direction", [SortingDirection.ASC, SortingDirection.DESC])
@pytest.mark.anyio
async def test_base_list_action_sort_direction(
    base_list_action: BaseListAction[DummyModel],
    direction: SortingDirection,
    mocker: MockerFixture,
) -> None:
    spy = mocker.spy(base_list_action._repository, "list")

    await base_list_action(sort_direction=direction)

    spy.assert_called_once_with(limit=None, offset=None, sort_attribute_name=None, sort_direction=direction)


@pytest.mark.parametrize(
    "limit, offset",
    [(10, 0), (5, 0), (10, 10), (20, 0)],
)
@pytest.mark.anyio
async def test_base_list_action_limit_offset(
    base_list_action: BaseListAction[DummyModel],
    limit: int,
    offset: int,
    mocker: MockerFixture,
) -> None:
    spy = mocker.spy(base_list_action._repository, "list")

    await base_list_action(limit=limit, offset=offset)

    spy.assert_called_once_with(limit=limit, offset=offset, sort_attribute_name=None, sort_direction=None)


@pytest.mark.parametrize(
    "limit, offset, name",
    [(10, 0, "name"), (5, 0, "another_name"), (10, 10, "yet_another_name"), (20, 0, "last_name")],
)
@pytest.mark.anyio
async def test_base_list_action_limit_offset_sort_attribute_name(
    base_list_action: BaseListAction[DummyModel],
    limit: int,
    offset: int,
    name: str,
    mocker: MockerFixture,
) -> None:
    spy = mocker.spy(base_list_action._repository, "list")

    await base_list_action(limit=limit, offset=offset, sort_attribute_name=name)

    spy.assert_called_once_with(limit=limit, offset=offset, sort_attribute_name=name, sort_direction=None)


@pytest.mark.parametrize(
    "limit, offset, name, direction",
    [
        (10, 0, "name", SortingDirection.ASC),
        (5, 0, "another_name", SortingDirection.DESC),
        (10, 10, "yet_another_name", SortingDirection.ASC),
        (20, 0, "last_name", SortingDirection.DESC),
    ],
)
@pytest.mark.anyio
async def test_base_list_action_limit_offset_sort_attribute_name_sort_direction(
    base_list_action: BaseListAction[DummyModel],
    limit: int,
    offset: int,
    name: str,
    direction: SortingDirection,
    mocker: MockerFixture,
) -> None:
    spy = mocker.spy(base_list_action._repository, "list")

    await base_list_action(limit=limit, offset=offset, sort_attribute_name=name, sort_direction=direction)

    spy.assert_called_once_with(limit=limit, offset=offset, sort_attribute_name=name, sort_direction=direction)


@pytest.mark.parametrize("pk", [1, 2, 3, 4, 5])
@pytest.mark.anyio
async def test_base_retrieve_action(pk: int, mocker: MockerFixture) -> None:
    action: BaseRetrieveAction[DummyModel] = BaseRetrieveAction(Mock(BaseRepository))

    spy = mocker.spy(action._repository, "retrieve")

    await action(pk=pk)

    spy.assert_called_once_with(pk=pk)


@pytest.mark.parametrize("pk", [1, 2, 3, 4, 5])
@pytest.mark.anyio
async def test_base_delete_action(pk: int, mocker: MockerFixture) -> None:
    action: BaseDeleteAction[DummyModel] = BaseDeleteAction(Mock(BaseRepository))

    spy = mocker.spy(action._repository, "delete")

    await action(pk=pk)

    spy.assert_called_once_with(pk=pk)


@pytest.mark.anyio
async def test_base_update_action(mocker: MockerFixture) -> None:
    action: BaseUpdateAction[DummyModel] = BaseUpdateAction(Mock(BaseRepository))

    spy = mocker.spy(action._repository, "save")

    dummy = DummyModel()

    mocker.patch.object(action._repository, "retrieve", return_value=dummy)

    output = await action(101, {"name": "new name"})

    spy.assert_called_once_with(dummy)
    assert output.name == "new name"


@pytest.mark.anyio
async def test_base_delete_action_not_found(mocker: MockerFixture) -> None:
    action: BaseUpdateAction[DummyModel] = BaseUpdateAction(Mock(BaseRepository))

    mocker.patch.object(action._repository, "retrieve", return_value=None)
    with pytest.raises(NotFoundException) as exc_info:
        await action(101, {"name": "new name"})
