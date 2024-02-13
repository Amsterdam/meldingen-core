import pytest
import pytest_asyncio

from meldingen_core.actions import MeldingCreateAction, MeldingListAction, MeldingRetrieveAction
from meldingen_core.models import Melding
from meldingen_core.repositories import BaseMeldingRepository

# Fixtures


@pytest.fixture
def unpopulated_meldingen_repository() -> BaseMeldingRepository:
    class TestMeldingRepository(BaseMeldingRepository):
        data: list[Melding]

        def __init__(self) -> None:
            self.data = []

        async def add(self, melding: Melding) -> None:
            self.data.append(melding)

        async def list(self, *, limit: int | None = None, offset: int | None = None) -> list[Melding]:
            if limit and offset:
                return self.data[offset : offset + limit]
            elif limit and not offset:
                return self.data[:limit]
            elif not limit and offset:
                return self.data[offset:]
            else:
                return self.data

        async def retrieve(self, pk: int) -> Melding | None:
            for _melding in self.data:
                if _melding.text == str(pk):
                    return _melding
            return None

    repository = TestMeldingRepository()
    return repository


@pytest_asyncio.fixture
async def populated_meldingen_repository(
    unpopulated_meldingen_repository: BaseMeldingRepository,
) -> BaseMeldingRepository:
    for _pk in range(10):
        melding = Melding()
        melding.text = f"{_pk}"
        await unpopulated_meldingen_repository.add(melding)

    return unpopulated_meldingen_repository


@pytest.fixture
def meldingen_create_action(
    unpopulated_meldingen_repository: BaseMeldingRepository,
) -> MeldingCreateAction:
    return MeldingCreateAction(unpopulated_meldingen_repository)


@pytest.fixture
def meldingen_list_action(
    populated_meldingen_repository: BaseMeldingRepository,
) -> MeldingListAction:
    return MeldingListAction(populated_meldingen_repository)


@pytest.fixture
def meldingen_retrieve_action(
    populated_meldingen_repository: BaseMeldingRepository,
) -> MeldingRetrieveAction:
    return MeldingRetrieveAction(populated_meldingen_repository)


# PyTest Classes


class TestMeldingCreateAction:
    @pytest.mark.asyncio
    async def test_add(self, meldingen_create_action: MeldingCreateAction) -> None:
        assert len(await meldingen_create_action.repository.list()) == 0

        melding = Melding()
        melding.text = "1"

        await meldingen_create_action(melding)

        assert len(await meldingen_create_action.repository.list()) == 1
        assert await meldingen_create_action.repository.retrieve(pk=1) == melding


class TestMeldingListAction:
    @pytest.mark.asyncio
    async def test_list_all(self, meldingen_list_action: MeldingListAction) -> None:
        meldingen = await meldingen_list_action()

        assert len(meldingen) == 10

    @pytest.mark.parametrize(
        "limit, expected_result",
        [(1, 1), (5, 5), (10, 10), (20, 10)],
    )
    @pytest.mark.asyncio
    async def test_list_limit(self, meldingen_list_action: MeldingListAction, limit: int, expected_result: int) -> None:
        meldingen = await meldingen_list_action(limit=limit)

        assert len(meldingen) == expected_result

    @pytest.mark.parametrize("offset, expected_result", [(1, 9), (5, 5), (10, 0), (20, 0)])
    @pytest.mark.asyncio
    async def test_list_offset(
        self,
        meldingen_list_action: MeldingListAction,
        offset: int,
        expected_result: int,
    ) -> None:
        meldingen = await meldingen_list_action(offset=offset)

        assert len(meldingen) == expected_result

    @pytest.mark.parametrize(
        "limit, offset, expected_result",
        [(10, 0, 10), (5, 0, 5), (10, 10, 0), (20, 0, 10)],
    )
    @pytest.mark.asyncio
    async def test_list_limit_offset(
        self,
        meldingen_list_action: MeldingListAction,
        limit: int,
        offset: int,
        expected_result: int,
    ) -> None:
        meldingen = await meldingen_list_action(limit=limit, offset=offset)

        assert len(meldingen) == expected_result


class TestMeldingRetrieveAction:
    @pytest.mark.parametrize("pk", [1, 2, 3, 4, 5])
    @pytest.mark.asyncio
    async def test_retrieve_existing_meldingen(self, meldingen_retrieve_action: MeldingRetrieveAction, pk: int) -> None:
        melding = await meldingen_retrieve_action(pk=pk)

        assert melding is not None
        assert melding.text == str(pk)

    @pytest.mark.parametrize("pk", [101, 102, 103, 104, 105])
    @pytest.mark.asyncio
    async def test_retrieve_non_existing_meldingen(
        self, meldingen_retrieve_action: MeldingRetrieveAction, pk: int
    ) -> None:
        melding = await meldingen_retrieve_action(pk=pk)

        assert melding is None
