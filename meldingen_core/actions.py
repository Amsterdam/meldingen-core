from meldingen_core.models import Melding
from meldingen_core.repositories import BaseMeldingRepository


class MeldingCreateAction:
    """Action that stores a melding."""

    repository: BaseMeldingRepository

    def __init__(self, repository: BaseMeldingRepository):
        self.repository = repository

    def __call__(self, melding: Melding) -> None:
        self.repository.add(melding)
