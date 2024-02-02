from meldingen_core.models import Melding
from meldingen_core.repositories import BaseMeldingRepository


class MeldingCreateAction:
    """Action that stores a melding."""

    repository: BaseMeldingRepository

    def __init__(self, repository: BaseMeldingRepository):
        self.repository = repository

    def __call__(self, melding: Melding) -> None:
        self.repository.add(melding)


class MeldingListAction:
    """Action that retrieves a list of meldingen."""

    repository: BaseMeldingRepository

    def __init__(self, repository: BaseMeldingRepository):
        self.repository = repository

    def __call__(self, *, limit: int | None = None, offset: int | None = None) -> list[Melding]:
        return self.repository.list(limit=limit, offset=offset)


class MeldingRetrieveAction:
    """Action that retrieves a melding."""

    repository: BaseMeldingRepository

    def __init__(self, repository: BaseMeldingRepository):
        self.repository = repository

    def __call__(self, pk: int) -> Melding | None:
        return self.repository.retrieve(pk=pk)
