from unittest.mock import AsyncMock, Mock

import pytest

from meldingen_core.actions.note import NoteCreateAction
from meldingen_core.exceptions import NotFoundException
from meldingen_core.factories import BaseNoteFactory
from meldingen_core.models import Melding, Note, User
from meldingen_core.repositories import BaseMeldingRepository, BaseNoteRepository


def test_can_instantiate_note_create_action() -> None:
    action: NoteCreateAction[Note, Melding, User] = NoteCreateAction(
        Mock(BaseNoteRepository), Mock(BaseMeldingRepository), Mock(BaseNoteFactory)
    )
    assert isinstance(action, NoteCreateAction)


@pytest.mark.anyio
async def test_note_create_action() -> None:
    melding = Melding(text="melding")
    user = User(username="behandelaar", email="behandelaar@example.com")
    note = Mock(Note)

    note_repository = Mock(BaseNoteRepository)
    note_repository.save = AsyncMock()
    melding_repository = Mock(BaseMeldingRepository)
    melding_repository.retrieve = AsyncMock(return_value=melding)
    note_factory = Mock(BaseNoteFactory, return_value=note)

    action: NoteCreateAction[Note, Melding, User] = NoteCreateAction(
        note_repository, melding_repository, note_factory
    )

    result = await action(123, "a note", user)

    assert result is note
    melding_repository.retrieve.assert_awaited_once_with(123)
    note_factory.assert_called_once_with("a note", melding, user)
    note_repository.save.assert_awaited_once_with(note)


@pytest.mark.anyio
async def test_note_create_action_raises_not_found_when_melding_does_not_exist() -> None:
    user = User(username="behandelaar", email="behandelaar@example.com")

    note_repository = Mock(BaseNoteRepository)
    note_repository.save = AsyncMock()
    melding_repository = Mock(BaseMeldingRepository)
    melding_repository.retrieve = AsyncMock(return_value=None)
    note_factory = Mock(BaseNoteFactory)

    action: NoteCreateAction[Note, Melding, User] = NoteCreateAction(
        note_repository, melding_repository, note_factory
    )

    with pytest.raises(NotFoundException):
        await action(123, "a note", user)

    note_factory.assert_not_called()
    note_repository.save.assert_not_awaited()
