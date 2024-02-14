from collections.abc import Collection

from meldingen_core.models import Melding
from meldingen_core.repositories import BaseMeldingRepository


class MeldingCreateAction:
    """Action that stores a melding."""

    repository: BaseMeldingRepository

    def __init__(self, repository: BaseMeldingRepository):
        self.repository = repository

    async def __call__(self, melding: Melding) -> None:
        await self.repository.save(melding)


class MeldingListAction:
    """Action that retrieves a list of meldingen."""

    repository: BaseMeldingRepository

    def __init__(self, repository: BaseMeldingRepository):
        self.repository = repository

    async def __call__(self, *, limit: int | None = None, offset: int | None = None) -> Collection[Melding]:
        return await self.repository.list(limit=limit, offset=offset)


class MeldingRetrieveAction:
    """Action that retrieves a melding."""

    repository: BaseMeldingRepository

    def __init__(self, repository: BaseMeldingRepository):
        self.repository = repository

    async def __call__(self, pk: int) -> Melding | None:
        return await self.repository.retrieve(pk=pk)
