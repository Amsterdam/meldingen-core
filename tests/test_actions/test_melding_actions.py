import logging
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest
from _pytest.logging import LogCaptureFixture

from meldingen_core.actions.melding import (
    MeldingAddAttachmentsAction,
    MeldingAddContactInfoAction,
    MeldingAnswerQuestionsAction,
    MeldingCompleteAction,
    MeldingContactInfoAddedAction,
    MeldingCreateAction,
    MeldingListAction,
    MeldingListQuestionsAnswersAction,
    MeldingProcessAction,
    MeldingRetrieveAction,
    MeldingSubmitAction,
    MeldingSubmitLocationAction,
    MeldingUpdateAction,
)
from meldingen_core.classification import ClassificationNotFoundException, Classifier
from meldingen_core.exceptions import NotFoundException
from meldingen_core.models import Answer, Classification, Melding
from meldingen_core.repositories import BaseAnswerRepository, BaseMeldingRepository
from meldingen_core.statemachine import BaseMeldingStateMachine, MeldingTransitions
from meldingen_core.token import BaseTokenGenerator, BaseTokenInvalidator, TokenVerifier


@pytest.mark.anyio
async def test_melding_create_action() -> None:
    classification = Classification(name="test")
    classifier = AsyncMock(Classifier, return_value=classification)
    state_machine = Mock(BaseMeldingStateMachine)
    repository = Mock(BaseMeldingRepository)
    action: MeldingCreateAction[Melding] = MeldingCreateAction(
        repository, classifier, state_machine, AsyncMock(BaseTokenGenerator), timedelta(days=3)
    )
    melding = Melding("text")

    await action(melding)

    assert repository.save.await_count == 2
    classifier.assert_awaited_once()
    state_machine.transition.assert_awaited_once()
    assert melding.classification == classification


@pytest.mark.anyio
async def test_melding_create_action_with_classification_not_found(caplog: LogCaptureFixture) -> None:
    classifier = AsyncMock(Classifier, side_effect=ClassificationNotFoundException)
    state_machine = Mock(BaseMeldingStateMachine)
    repository = Mock(BaseMeldingRepository)
    action: MeldingCreateAction[Melding] = MeldingCreateAction(
        repository, classifier, state_machine, AsyncMock(BaseTokenGenerator), timedelta(days=3)
    )
    melding = Melding("text")

    with caplog.at_level(logging.ERROR):
        await action(melding)

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "ERROR"
    assert caplog.records[0].message == "Classifier failed to find classification!"

    state_machine.transition.assert_not_awaited()


def test_can_instantiate_melding_list_action() -> None:
    action: MeldingListAction[Melding] = MeldingListAction(Mock(BaseMeldingRepository))
    assert isinstance(action, MeldingListAction)


def test_can_instantiate_melding_retrieve_action() -> None:
    action: MeldingRetrieveAction[Melding] = MeldingRetrieveAction(Mock(BaseMeldingRepository))
    assert isinstance(action, MeldingRetrieveAction)


@pytest.mark.anyio
async def test_melding_update_action() -> None:
    token = "123456"
    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = Melding("text", token=token, token_expires=datetime.now() + timedelta(days=1))
    token_verifier = AsyncMock(TokenVerifier)
    classification = Classification(name="test")
    classifier = AsyncMock(Classifier, return_value=classification)
    action: MeldingUpdateAction[Melding] = MeldingUpdateAction(
        repository, token_verifier, classifier, Mock(BaseMeldingStateMachine)
    )

    text = "new text"
    melding = await action(123, {"text": text}, token)

    assert melding.text == text
    assert melding.classification == classification


@pytest.mark.anyio
async def test_melding_add_contact_action() -> None:
    token = "123456"
    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = Melding("text", token=token, token_expires=datetime.now() + timedelta(days=1))
    token_verifier = AsyncMock(TokenVerifier)

    action: MeldingAddContactInfoAction[Melding] = MeldingAddContactInfoAction(repository, token_verifier)

    phone = "1234567"
    email = "user@test.com"
    melding = await action(123, phone, email, token)

    assert melding.phone == phone
    assert melding.email == email


@pytest.mark.anyio
async def test_melding_add_contact_action_not_found() -> None:
    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = None
    token_verifier: TokenVerifier[Melding] = TokenVerifier(repository)

    action: MeldingAddContactInfoAction[Melding] = MeldingAddContactInfoAction(repository, token_verifier)

    with pytest.raises(NotFoundException):
        await action(123, "1234567", "user@test.com", "token")


@pytest.mark.anyio
async def test_melding_answer_questions_action() -> None:
    state_machine = Mock(BaseMeldingStateMachine)
    repo_melding = Melding("melding text")
    repository = Mock(BaseMeldingRepository)

    token_verifier = AsyncMock(TokenVerifier)
    token_verifier.return_value = repo_melding

    answer_questions: MeldingAnswerQuestionsAction[Melding] = MeldingAnswerQuestionsAction(
        state_machine, repository, token_verifier
    )

    melding = await answer_questions(123, "token")

    assert melding == repo_melding
    state_machine.transition.assert_awaited_once_with(repo_melding, MeldingTransitions.ANSWER_QUESTIONS)
    repository.save.assert_awaited_once_with(repo_melding)
    token_verifier.assert_awaited_once()


@pytest.mark.anyio
async def test_process_action() -> None:
    state_machine = Mock(BaseMeldingStateMachine)
    repo_melding = Melding("melding text")
    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = repo_melding
    process: MeldingProcessAction[Melding] = MeldingProcessAction(state_machine, repository)

    melding = await process(1)

    assert melding == repo_melding
    state_machine.transition.assert_called_once_with(repo_melding, MeldingTransitions.PROCESS)
    repository.save.assert_called_once_with(repo_melding)


@pytest.mark.anyio
async def test_process_action_not_found() -> None:
    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = None

    process: MeldingProcessAction[Melding] = MeldingProcessAction(Mock(BaseMeldingStateMachine), repository)

    with pytest.raises(NotFoundException):
        await process(1)


@pytest.mark.anyio
async def test_add_attachments_action() -> None:
    repository = Mock(BaseMeldingRepository)
    repo_melding = Melding("melding text")
    repository.retrieve.return_value = repo_melding
    state_machine = Mock(BaseMeldingStateMachine)
    token_verifier = AsyncMock(TokenVerifier)
    token_verifier.return_value = repo_melding

    add_attachments: MeldingAddAttachmentsAction[Melding] = MeldingAddAttachmentsAction(
        state_machine, repository, token_verifier
    )

    melding = await add_attachments(1, "token")

    assert melding == repo_melding
    state_machine.transition.assert_called_once_with(repo_melding, MeldingTransitions.ADD_ATTACHMENTS)
    repository.save.assert_called_once_with(repo_melding)


@pytest.mark.anyio
async def test_add_attachments_action_not_found() -> None:
    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = None
    token_verifier: TokenVerifier[Melding] = TokenVerifier(repository)

    process: MeldingAddAttachmentsAction[Melding] = MeldingAddAttachmentsAction(
        Mock(BaseMeldingStateMachine), Mock(BaseMeldingRepository), token_verifier
    )

    with pytest.raises(NotFoundException):
        await process(1, "token")


@pytest.mark.anyio
async def test_complete_action() -> None:
    state_machine = Mock(BaseMeldingStateMachine)
    repo_melding = Melding("melding text")
    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = repo_melding
    process: MeldingCompleteAction[Melding] = MeldingCompleteAction(state_machine, repository)

    melding = await process(1)

    assert melding == repo_melding
    state_machine.transition.assert_called_once_with(repo_melding, MeldingTransitions.COMPLETE)
    repository.save.assert_called_once_with(repo_melding)


@pytest.mark.anyio
async def test_complete_action_not_found() -> None:
    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = None

    process: MeldingCompleteAction[Melding] = MeldingCompleteAction(Mock(BaseMeldingStateMachine), repository)

    with pytest.raises(NotFoundException):
        await process(1)


@pytest.mark.anyio
async def test_submit_location_action() -> None:
    repository = Mock(BaseMeldingRepository)
    repo_melding = Melding("melding text")
    repository.retrieve.return_value = repo_melding
    state_machine = Mock(BaseMeldingStateMachine)
    token_verifier = AsyncMock(TokenVerifier)
    token_verifier.return_value = repo_melding

    submit_location: MeldingSubmitLocationAction[Melding] = MeldingSubmitLocationAction(
        state_machine, repository, token_verifier
    )

    melding = await submit_location(1, "token")

    assert melding == repo_melding
    state_machine.transition.assert_called_once_with(repo_melding, MeldingTransitions.SUBMIT_LOCATION)
    repository.save.assert_called_once_with(repo_melding)


@pytest.mark.anyio
async def test_submit_location_action_not_found() -> None:
    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = None
    token_verifier: TokenVerifier[Melding] = TokenVerifier(repository)

    process: MeldingSubmitLocationAction[Melding] = MeldingSubmitLocationAction(
        Mock(BaseMeldingStateMachine), Mock(BaseMeldingRepository), token_verifier
    )

    with pytest.raises(NotFoundException):
        await process(1, "token")


@pytest.mark.anyio
async def test_contact_info_added_action() -> None:
    repository = Mock(BaseMeldingRepository)
    repo_melding = Melding("melding text")
    repository.retrieve.return_value = repo_melding
    state_machine = Mock(BaseMeldingStateMachine)
    token_verifier = AsyncMock(TokenVerifier)
    token_verifier.return_value = repo_melding

    add_contact_info: MeldingContactInfoAddedAction[Melding] = MeldingContactInfoAddedAction(
        state_machine, repository, token_verifier
    )

    melding = await add_contact_info(1, "token")

    assert melding == repo_melding
    state_machine.transition.assert_called_once_with(repo_melding, MeldingTransitions.ADD_CONTACT_INFO)
    repository.save.assert_called_once_with(repo_melding)


@pytest.mark.anyio
async def test_contact_info_added_action_not_found() -> None:
    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = None
    state_machine = Mock(BaseMeldingStateMachine)
    token_verifier: TokenVerifier[Melding] = TokenVerifier(repository)

    add_contact_info: MeldingContactInfoAddedAction[Melding] = MeldingContactInfoAddedAction(
        state_machine, repository, token_verifier
    )

    with pytest.raises(NotFoundException):
        await add_contact_info(1, "token")


@pytest.mark.anyio
async def test_list_answers() -> None:
    repository = Mock(BaseAnswerRepository)
    repository.find_by_melding.return_value = []

    repo_melding = Melding("melding text")
    repository.retrieve.return_value = repo_melding
    token_verifier = AsyncMock(TokenVerifier)
    token_verifier.return_value = repo_melding

    action: MeldingListQuestionsAnswersAction[Melding, Answer] = MeldingListQuestionsAnswersAction(
        token_verifier, repository
    )

    answers = await action(1, "token")
    assert answers == []


@pytest.mark.anyio
async def test_submit_melding() -> None:
    repo_melding = Melding("text")
    state_machine = Mock(BaseMeldingStateMachine)
    repository = Mock(BaseMeldingRepository)
    token_verifier = AsyncMock(TokenVerifier)

    token_verifier.return_value = repo_melding
    token_invalidator = AsyncMock(BaseTokenInvalidator)

    action: MeldingSubmitAction[Melding] = MeldingSubmitAction(
        repository, state_machine, token_verifier, token_invalidator
    )

    melding = await action(1, "token")
    assert melding == repo_melding

    state_machine.transition.assert_called_once_with(repo_melding, MeldingTransitions.SUBMIT)
    token_invalidator.assert_called_once_with(repo_melding)
    repository.save.assert_called_once_with(repo_melding)
