from collections.abc import Sequence

from meldingen_core import SortingDirection
from meldingen_core.exceptions import NotFoundException
from meldingen_core.factories import BaseNoteFactory
from meldingen_core.models import Melding, Note, User
from meldingen_core.repositories import BaseMeldingRepository, BaseNoteRepository
from meldingen_core.repository_helpers import retrieve_or_raise_not_found


class NoteCreateAction[N: Note, T: Melding, U: User]:
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
        melding = await retrieve_or_raise_not_found(self._melding_repository, melding_id)

        note = self._note_factory(text, melding, user)
        await self._note_repository.save(note)

        return note


class NoteRetrieveAction[N: Note]:
    """Action that retrieves a single note belonging to a melding."""

    _note_repository: BaseNoteRepository[N]

    def __init__(self, note_repository: BaseNoteRepository[N]) -> None:
        self._note_repository = note_repository

    async def __call__(self, melding_id: int, note_id: int) -> N:
        note = await self._note_repository.find_by_id_and_melding(note_id, melding_id)
        if note is None:
            raise NotFoundException()

        return note


class NoteListAction[N: Note, T: Melding]:
    """Action that lists the notes belonging to a melding."""

    _note_repository: BaseNoteRepository[N]
    _melding_repository: BaseMeldingRepository[T]

    def __init__(
        self,
        note_repository: BaseNoteRepository[N],
        melding_repository: BaseMeldingRepository[T],
    ) -> None:
        self._note_repository = note_repository
        self._melding_repository = melding_repository

    async def __call__(
        self,
        melding_id: int,
        *,
        sort_attribute_name: str | None = None,
        sort_direction: SortingDirection | None = None,
    ) -> Sequence[N]:
        # Just make sure the melding exists before listing its notes.
        await retrieve_or_raise_not_found(self._melding_repository, melding_id)

        return await self._note_repository.find_by_melding(
            melding_id,
            sort_attribute_name=sort_attribute_name,
            sort_direction=sort_direction,
        )


class NoteUpdateAction[N: Note]:
    """Action that updates the text of a note belonging to a melding.

    Whether the acting user is allowed to update the note (e.g. ownership) is the
    responsibility of the caller.
    """

    _note_repository: BaseNoteRepository[N]

    def __init__(self, note_repository: BaseNoteRepository[N]) -> None:
        self._note_repository = note_repository

    async def __call__(self, melding_id: int, note_id: int, text: str) -> N:
        note = await self._note_repository.find_by_id_and_melding(note_id, melding_id)
        if note is None:
            raise NotFoundException()

        note.text = text
        await self._note_repository.save(note)

        return note
