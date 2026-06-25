from typing import Generic, TypeVar

from meldingen_core.exceptions import NotFoundException
from meldingen_core.factories import BaseNoteFactory
from meldingen_core.models import Melding, Note, User
from meldingen_core.repositories import BaseMeldingRepository, BaseNoteRepository

N = TypeVar("N", bound=Note)
T = TypeVar("T", bound=Melding)
U = TypeVar("U", bound=User)


class NoteCreateAction(Generic[N, T, U]):
    """Action that stores a note on a melding."""

    _note_repository: BaseNoteRepository[N]
    _melding_repository: BaseMeldingRepository[T]
    _note_factory: BaseNoteFactory[N, T, U]

    def __init__(
        self,
        note_repository: BaseNoteRepository[N],
        melding_repository: BaseMeldingRepository[T],
        note_factory: BaseNoteFactory[N, T, U],
    ) -> None:
        self._note_repository = note_repository
        self._melding_repository = melding_repository
        self._note_factory = note_factory

    async def __call__(self, melding_id: int, text: str, user: U) -> N:
        melding = await self._melding_repository.retrieve(melding_id)
        if melding is None:
            raise NotFoundException()

        note = self._note_factory(text, melding, user)
        await self._note_repository.save(note)

        return note
