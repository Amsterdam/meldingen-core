from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from meldingen_core.actions.melding import (
    MeldingAnswerQuestionsAction,
    MeldingCompleteAction,
    MeldingCreateAction,
    MeldingListAction,
    MeldingProcessAction,
    MeldingRetrieveAction,
    MeldingUpdateAction,
)
from meldingen_core.classification import Classifier
from meldingen_core.exceptions import NotFoundException
from meldingen_core.models import Classification, Melding
from meldingen_core.repositories import BaseMeldingRepository
from meldingen_core.statemachine import BaseMeldingStateMachine, MeldingTransitions
from meldingen_core.token import BaseTokenGenerator, TokenVerifier


@pytest.mark.asyncio
async def test_melding_create_action() -> None:
    classification = Classification(name="test")
    classifier = AsyncMock(Classifier, return_value=classification)
    state_machine = Mock(BaseMeldingStateMachine)
    repository = Mock(BaseMeldingRepository)
    action: MeldingCreateAction[Melding, Melding] = MeldingCreateAction(
        repository, classifier, state_machine, AsyncMock(BaseTokenGenerator), timedelta(days=3)
    )
    melding = Melding("text")

    await action(melding)

    assert repository.save.await_count == 2
    classifier.assert_awaited_once()
    state_machine.transition.assert_awaited_once()
    assert melding.classification == classification


def test_can_instantiate_melding_list_action() -> None:
    action: MeldingListAction[Melding, Melding] = MeldingListAction(Mock(BaseMeldingRepository))
    assert isinstance(action, MeldingListAction)


def test_can_instantiate_melding_retrieve_action() -> None:
    action: MeldingRetrieveAction[Melding, Melding] = MeldingRetrieveAction(Mock(BaseMeldingRepository))
    assert isinstance(action, MeldingRetrieveAction)


@pytest.mark.asyncio
async def test_melding_update_action_not_found() -> None:
    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = None
    token_verifier = MagicMock(TokenVerifier)
    action: MeldingUpdateAction[Melding, Melding] = MeldingUpdateAction(
        repository, token_verifier, AsyncMock(Classifier), Mock(BaseMeldingStateMachine)
    )

    with pytest.raises(NotFoundException):
        await action(123, {"text": "test"}, "123456")


@pytest.mark.asyncio
async def test_melding_update_action() -> None:
    token = "123456"
    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = Melding("text", token=token, token_expires=datetime.now() + timedelta(days=1))
    token_verifier = MagicMock(TokenVerifier)
    classification = Classification(name="test")
    classifier = AsyncMock(Classifier, return_value=classification)
    action: MeldingUpdateAction[Melding, Melding] = MeldingUpdateAction(
        repository, token_verifier, classifier, Mock(BaseMeldingStateMachine)
    )

    text = "new text"
    melding = await action(123, {"text": text}, token)

    assert melding.text == text
    assert melding.classification == classification


@pytest.mark.asyncio
async def test_melding_answer_questions_action() -> None:
    state_machine = Mock(BaseMeldingStateMachine)
    repo_melding = Melding("melding text")
    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = repo_melding
    token_verifier = MagicMock(TokenVerifier)
    answer_questions: MeldingAnswerQuestionsAction[Melding, Melding] = MeldingAnswerQuestionsAction(
        state_machine, repository, token_verifier
    )

    melding = await answer_questions(123, "token")

    assert melding == repo_melding
    state_machine.transition.assert_awaited_once_with(repo_melding, MeldingTransitions.ANSWER_QUESTIONS)
    repository.save.assert_awaited_once_with(repo_melding)
    token_verifier.assert_called_once_with(repo_melding, "token")


@pytest.mark.asyncio
async def test_melding_answer_questions_action_not_found() -> None:
    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = None

    answer_questions: MeldingAnswerQuestionsAction[Melding, Melding] = MeldingAnswerQuestionsAction(
        Mock(BaseMeldingStateMachine), repository, Mock(TokenVerifier)
    )
    with pytest.raises(NotFoundException):
        await answer_questions(1, "token")


@pytest.mark.asyncio
async def test_process_action() -> None:
    state_machine = Mock(BaseMeldingStateMachine)
    repo_melding = Melding("melding text")
    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = repo_melding
    process: MeldingProcessAction[Melding, Melding] = MeldingProcessAction(state_machine, repository)

    melding = await process(1)

    assert melding == repo_melding
    state_machine.transition.assert_called_once_with(repo_melding, MeldingTransitions.PROCESS)
    repository.save.assert_called_once_with(repo_melding)


@pytest.mark.asyncio
async def test_process_action_not_found() -> None:
    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = None

    process: MeldingProcessAction[Melding, Melding] = MeldingProcessAction(Mock(BaseMeldingStateMachine), repository)

    with pytest.raises(NotFoundException):
        await process(1)


@pytest.mark.asyncio
async def test_complete_action() -> None:
    state_machine = Mock(BaseMeldingStateMachine)
    repo_melding = Melding("melding text")
    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = repo_melding
    process: MeldingCompleteAction[Melding, Melding] = MeldingCompleteAction(state_machine, repository)

    melding = await process(1)

    assert melding == repo_melding
    state_machine.transition.assert_called_once_with(repo_melding, MeldingTransitions.COMPLETE)
    repository.save.assert_called_once_with(repo_melding)


@pytest.mark.asyncio
async def test_complete_action_not_found() -> None:
    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = None

    process: MeldingCompleteAction[Melding, Melding] = MeldingCompleteAction(Mock(BaseMeldingStateMachine), repository)

    with pytest.raises(NotFoundException):
        await process(1)
