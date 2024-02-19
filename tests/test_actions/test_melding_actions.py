from collections.abc import Collection

import pytest
from pytest_mock import MockerFixture

from meldingen_core.actions.melding import MeldingCreateAction, MeldingListAction, MeldingRetrieveAction
from meldingen_core.models import Melding
from meldingen_core.repositories import BaseMeldingRepository

# Fixtures


@pytest.fixture
def mocked_repository() -> BaseMeldingRepository:
    class MockMeldingRepository(BaseMeldingRepository):
        async def save(self, obj: Melding) -> None:
            return None

        async def list(self, *, limit: int | None = None, offset: int | None = None) -> Collection[Melding]:
            return []

        async def retrieve(self, pk: int) -> Melding | None:
            return None

        async def delete(self, pk: int) -> None: # pragma: no cover
            return None

    mocked_repository = MockMeldingRepository()
    return mocked_repository


@pytest.fixture
def meldingen_create_action(
    mocked_repository: BaseMeldingRepository,
) -> MeldingCreateAction:
    return MeldingCreateAction(mocked_repository)


@pytest.fixture
def meldingen_list_action(
    mocked_repository: BaseMeldingRepository,
) -> MeldingListAction:
    return MeldingListAction(mocked_repository)


@pytest.fixture
def meldingen_retrieve_action(
    mocked_repository: BaseMeldingRepository,
) -> MeldingRetrieveAction:
    return MeldingRetrieveAction(mocked_repository)


# PyTest Classes


class TestMeldingCreateAction:
    @pytest.mark.asyncio
    async def test_add(self, meldingen_create_action: MeldingCreateAction, mocker: MockerFixture) -> None:
        spy = mocker.spy(meldingen_create_action._repository, "save")

        melding = Melding()
        melding.text = "1"

        await meldingen_create_action(melding)

        spy.assert_called_once_with(melding)


class TestMeldingListAction:
    @pytest.mark.asyncio
    async def test_list_all(self, meldingen_list_action: MeldingListAction, mocker: MockerFixture) -> None:
        spy = mocker.spy(meldingen_list_action._repository, "list")

        meldingen = await meldingen_list_action()

        spy.assert_called_once()

    @pytest.mark.parametrize(
        "limit",
        [1, 5, 10, 20],
    )
    @pytest.mark.asyncio
    async def test_list_limit(
        self, meldingen_list_action: MeldingListAction, limit: int, mocker: MockerFixture
    ) -> None:
        spy = mocker.spy(meldingen_list_action._repository, "list")

        meldingen = await meldingen_list_action(limit=limit)

        spy.assert_called_once_with(limit=limit, offset=None)

    @pytest.mark.parametrize("offset", [1, 5, 10, 20])
    @pytest.mark.asyncio
    async def test_list_offset(
        self, meldingen_list_action: MeldingListAction, offset: int, mocker: MockerFixture
    ) -> None:
        spy = mocker.spy(meldingen_list_action._repository, "list")

        await meldingen_list_action(limit=None, offset=offset)

        spy.assert_called_once_with(limit=None, offset=offset)

    @pytest.mark.parametrize(
        "limit, offset",
        [(10, 0), (5, 0), (10, 10), (20, 0)],
    )
    @pytest.mark.asyncio
    async def test_list_limit_offset(
        self,
        meldingen_list_action: MeldingListAction,
        limit: int,
        offset: int,
        mocker: MockerFixture,
    ) -> None:
        spy = mocker.spy(meldingen_list_action._repository, "list")

        await meldingen_list_action(limit=limit, offset=offset)

        spy.assert_called_once_with(limit=limit, offset=offset)


class TestMeldingRetrieveAction:
    @pytest.mark.parametrize("pk", [1, 2, 3, 4, 5])
    @pytest.mark.asyncio
    async def test_retrieve_melding(
        self, meldingen_retrieve_action: MeldingRetrieveAction, pk: int, mocker: MockerFixture
    ) -> None:
        spy = mocker.spy(meldingen_retrieve_action._repository, "retrieve")

        await meldingen_retrieve_action(pk=pk)

        spy.assert_called_once_with(pk=pk)
