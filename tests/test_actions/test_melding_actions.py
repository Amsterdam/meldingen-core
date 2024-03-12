from unittest.mock import Mock

import pytest

from meldingen_core.actions.melding import (
    MeldingCompleteAction,
    MeldingCreateAction,
    MeldingListAction,
    MeldingProcessAction,
    MeldingRetrieveAction,
)
from meldingen_core.exceptions import NotFoundException
from meldingen_core.models import Melding
from meldingen_core.repositories import BaseMeldingRepository
from meldingen_core.statemachine import BaseMeldingStateMachine, MeldingTransitions


def test_can_instantiate_melding_create_action() -> None:
    action = MeldingCreateAction(Mock(BaseMeldingRepository))
    assert isinstance(action, MeldingCreateAction)


def test_can_instantiate_melding_list_action() -> None:
    action: MeldingListAction[Melding, Melding] = MeldingListAction(Mock(BaseMeldingRepository))
    assert isinstance(action, MeldingListAction)


def test_can_instantiate_melding_retrieve_action() -> None:
    action: MeldingRetrieveAction[Melding, Melding] = MeldingRetrieveAction(Mock(BaseMeldingRepository))
    assert isinstance(action, MeldingRetrieveAction)


@pytest.mark.asyncio
async def test_process_action() -> None:
    state_machine = Mock(BaseMeldingStateMachine)
    repo_melding = Melding("melding text")
    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = repo_melding
    process = MeldingProcessAction(state_machine, repository)

    melding = await process(1)

    assert melding == repo_melding
    state_machine.transition.assert_called_once_with(repo_melding, MeldingTransitions.PROCESS)
    repository.save.assert_called_once_with(repo_melding)


@pytest.mark.asyncio
async def test_process_action_not_found() -> None:
    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = None

    process = MeldingProcessAction(Mock(BaseMeldingStateMachine), repository)

    with pytest.raises(NotFoundException):
        await process(1)


@pytest.mark.asyncio
async def test_complete_action() -> None:
    state_machine = Mock(BaseMeldingStateMachine)
    repo_melding = Melding("melding text")
    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = repo_melding
    process = MeldingCompleteAction(state_machine, repository)

    melding = await process(1)

    assert melding == repo_melding
    state_machine.transition.assert_called_once_with(repo_melding, MeldingTransitions.COMPLETE)
    repository.save.assert_called_once_with(repo_melding)


@pytest.mark.asyncio
async def test_complete_action_not_found() -> None:
    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = None

    process = MeldingCompleteAction(Mock(BaseMeldingStateMachine), repository)

    with pytest.raises(NotFoundException):
        await process(1)
