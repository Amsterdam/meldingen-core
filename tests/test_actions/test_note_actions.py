from unittest.mock import AsyncMock, Mock

import pytest

from meldingen_core.actions.note import NoteCreateAction, NoteListAction, NoteRetrieveAction, NoteUpdateAction
from meldingen_core.exceptions import ForbiddenException, NotFoundException
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

    action: NoteCreateAction[Note, Melding, User] = NoteCreateAction(note_repository, melding_repository, note_factory)

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

    action: NoteCreateAction[Note, Melding, User] = NoteCreateAction(note_repository, melding_repository, note_factory)

    with pytest.raises(NotFoundException):
        await action(123, "a note", user)

    note_factory.assert_not_called()
    note_repository.save.assert_not_awaited()


def test_can_instantiate_note_retrieve_action() -> None:
    action: NoteRetrieveAction[Note] = NoteRetrieveAction(Mock(BaseNoteRepository))
    assert isinstance(action, NoteRetrieveAction)


@pytest.mark.anyio
async def test_note_retrieve_action() -> None:
    note = Mock(Note)
    note_repository = Mock(BaseNoteRepository)
    note_repository.find_by_id_and_melding = AsyncMock(return_value=note)

    action: NoteRetrieveAction[Note] = NoteRetrieveAction(note_repository)

    result = await action(5, 9)

    assert result is note
    note_repository.find_by_id_and_melding.assert_awaited_once_with(9, 5)


@pytest.mark.anyio
async def test_note_retrieve_action_raises_not_found_when_note_does_not_exist() -> None:
    note_repository = Mock(BaseNoteRepository)
    note_repository.find_by_id_and_melding = AsyncMock(return_value=None)

    action: NoteRetrieveAction[Note] = NoteRetrieveAction(note_repository)

    with pytest.raises(NotFoundException):
        await action(5, 9)


def test_can_instantiate_note_list_action() -> None:
    action: NoteListAction[Note, Melding] = NoteListAction(Mock(BaseNoteRepository), Mock(BaseMeldingRepository))
    assert isinstance(action, NoteListAction)


@pytest.mark.anyio
async def test_note_list_action() -> None:
    melding = Melding(text="melding")
    notes = [Mock(Note), Mock(Note)]

    note_repository = Mock(BaseNoteRepository)
    note_repository.find_by_melding = AsyncMock(return_value=notes)
    melding_repository = Mock(BaseMeldingRepository)
    melding_repository.retrieve = AsyncMock(return_value=melding)

    action: NoteListAction[Note, Melding] = NoteListAction(note_repository, melding_repository)

    result = await action(123)

    assert result is notes
    melding_repository.retrieve.assert_awaited_once_with(123)
    note_repository.find_by_melding.assert_awaited_once_with(123)


@pytest.mark.anyio
async def test_note_list_action_raises_not_found_when_melding_does_not_exist() -> None:
    note_repository = Mock(BaseNoteRepository)
    note_repository.find_by_melding = AsyncMock()
    melding_repository = Mock(BaseMeldingRepository)
    melding_repository.retrieve = AsyncMock(return_value=None)

    action: NoteListAction[Note, Melding] = NoteListAction(note_repository, melding_repository)

    with pytest.raises(NotFoundException):
        await action(123)

    note_repository.find_by_melding.assert_not_awaited()


def test_can_instantiate_note_update_action() -> None:
    action: NoteUpdateAction[Note, User] = NoteUpdateAction(Mock(BaseNoteRepository))
    assert isinstance(action, NoteUpdateAction)


@pytest.mark.anyio
async def test_note_update_action() -> None:
    user = User(username="behandelaar", email="behandelaar@example.com")
    note = Mock(Note)
    note.user = user

    note_repository = Mock(BaseNoteRepository)
    note_repository.find_by_id_and_melding = AsyncMock(return_value=note)
    note_repository.save = AsyncMock()

    action: NoteUpdateAction[Note, User] = NoteUpdateAction(note_repository)

    result = await action(5, 9, "updated text", user)

    assert result is note
    assert note.text == "updated text"
    note_repository.find_by_id_and_melding.assert_awaited_once_with(9, 5)
    note_repository.save.assert_awaited_once_with(note)


@pytest.mark.anyio
async def test_note_update_action_allows_empty_text() -> None:
    user = User(username="behandelaar", email="behandelaar@example.com")
    note = Mock(Note)
    note.user = user

    note_repository = Mock(BaseNoteRepository)
    note_repository.find_by_id_and_melding = AsyncMock(return_value=note)
    note_repository.save = AsyncMock()

    action: NoteUpdateAction[Note, User] = NoteUpdateAction(note_repository)

    await action(5, 9, "", user)

    assert note.text == ""
    note_repository.save.assert_awaited_once_with(note)


@pytest.mark.anyio
async def test_note_update_action_raises_not_found_when_note_does_not_exist() -> None:
    user = User(username="behandelaar", email="behandelaar@example.com")

    note_repository = Mock(BaseNoteRepository)
    note_repository.find_by_id_and_melding = AsyncMock(return_value=None)
    note_repository.save = AsyncMock()

    action: NoteUpdateAction[Note, User] = NoteUpdateAction(note_repository)

    with pytest.raises(NotFoundException):
        await action(5, 9, "text", user)

    note_repository.save.assert_not_awaited()


@pytest.mark.anyio
async def test_note_update_action_raises_forbidden_when_user_is_not_owner() -> None:
    owner = User(username="owner", email="owner@example.com")
    other = User(username="other", email="other@example.com")
    note = Mock(Note)
    note.user = owner

    note_repository = Mock(BaseNoteRepository)
    note_repository.find_by_id_and_melding = AsyncMock(return_value=note)
    note_repository.save = AsyncMock()

    action: NoteUpdateAction[Note, User] = NoteUpdateAction(note_repository)

    with pytest.raises(ForbiddenException):
        await action(5, 9, "text", other)

    note_repository.save.assert_not_awaited()
