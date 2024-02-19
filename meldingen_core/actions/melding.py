from collections.abc import Collection

from meldingen_core.actions.base import BaseCreateAction, BaseRetrieveAction
from meldingen_core.models import Melding
from meldingen_core.repositories import BaseMeldingRepository


class MeldingCreateAction(BaseCreateAction[Melding, Melding]):
    """Action that stores a melding."""


class MeldingListAction:
    """Action that retrieves a list of meldingen."""

    repository: BaseMeldingRepository

    def __init__(self, repository: BaseMeldingRepository):
        self.repository = repository

    async def __call__(self, *, limit: int | None = None, offset: int | None = None) -> Collection[Melding]:
        return await self.repository.list(limit=limit, offset=offset)


class MeldingRetrieveAction(BaseRetrieveAction[Melding, Melding]):
    """Action that retrieves a melding."""
