import logging
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest
from _pytest.logging import LogCaptureFixture

from meldingen_core import SortingDirection
from meldingen_core.actions.melding import (
    MelderMeldingListQuestionsAnswersAction,
    MeldingAddAssetAction,
    MeldingAddAttachmentsAction,
    MeldingAddContactInfoAction,
    MeldingAnswerQuestionsAction,
    MeldingCompleteAction,
    MeldingContactInfoAddedAction,
    MeldingCreateAction,
    MeldingDeleteAssetAction,
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
from meldingen_core.factories import BaseAssetFactory
from meldingen_core.filters import MeldingListFilters
from meldingen_core.mail import BaseMeldingCompleteMailer, BaseMeldingConfirmationMailer
from meldingen_core.managers import RelationshipManager
from meldingen_core.models import Answer, Asset, AssetType, Classification, Melding
from meldingen_core.reclassification import BaseReclassification
from meldingen_core.repositories import (
    BaseAnswerRepository,
    BaseAssetRepository,
    BaseAssetTypeRepository,
    BaseMeldingRepository,
)
from meldingen_core.statemachine import BaseMeldingStateMachine, MeldingStates, MeldingTransitions
from meldingen_core.token import BaseTokenGenerator, BaseTokenInvalidator, TokenVerifier


@pytest.mark.anyio
async def test_melding_create_action() -> None:
    classification = Classification(name="test")
    classifier = AsyncMock(Classifier, return_value=classification)
    state_machine = Mock(BaseMeldingStateMachine)
    repository = Mock(BaseMeldingRepository)
    action: MeldingCreateAction[Melding, Classification] = MeldingCreateAction(
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
    action: MeldingCreateAction[Melding, Classification] = MeldingCreateAction(
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


@pytest.mark.anyio
async def test_melding_list_action() -> None:
    repository = Mock(BaseMeldingRepository)
    action: MeldingListAction[Melding] = MeldingListAction(repository)
    filters: MeldingListFilters = MeldingListFilters(area="AREA", states=[MeldingStates.NEW, MeldingStates.SUBMITTED])

    await action(limit=10, offset=0, sort_attribute_name="attr", sort_direction=SortingDirection.ASC, filters=filters)

    repository.list_meldingen.assert_awaited_once()


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
    reclassifier = AsyncMock(BaseReclassification)

    action: MeldingUpdateAction[Melding, Classification] = MeldingUpdateAction(
        repository, token_verifier, classifier, Mock(BaseMeldingStateMachine), reclassifier
    )

    text = "new text"
    melding = await action(123, {"text": text}, token)

    assert melding.text == text
    assert melding.classification == classification


@pytest.mark.anyio
async def test_melding_update_action_with_classification_not_found() -> None:
    token = "123456"
    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = Melding("text", token=token, token_expires=datetime.now() + timedelta(days=1))
    token_verifier = AsyncMock(TokenVerifier)
    classifier = AsyncMock(Classifier, side_effect=ClassificationNotFoundException)
    reclassifier = AsyncMock(BaseReclassification)

    action: MeldingUpdateAction[Melding, Classification] = MeldingUpdateAction(
        repository, token_verifier, classifier, Mock(BaseMeldingStateMachine), reclassifier
    )

    text = "new text"
    melding = await action(123, {"text": text}, token)

    assert melding.text == text
    assert melding.classification is None


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
    complete: MeldingCompleteAction[Melding] = MeldingCompleteAction(
        state_machine, repository, AsyncMock(BaseMeldingCompleteMailer)
    )

    melding = await complete(1, "test mail text")

    assert melding == repo_melding
    state_machine.transition.assert_called_once_with(repo_melding, MeldingTransitions.COMPLETE)
    repository.save.assert_called_once_with(repo_melding)


@pytest.mark.anyio
async def test_complete_action_not_found() -> None:
    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = None

    process: MeldingCompleteAction[Melding] = MeldingCompleteAction(
        Mock(BaseMeldingStateMachine), repository, Mock(BaseMeldingCompleteMailer)
    )

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

    action: MelderMeldingListQuestionsAnswersAction[Melding, Answer] = MelderMeldingListQuestionsAnswersAction(
        token_verifier, repository
    )

    answers = await action(1, "token")
    assert answers == []


@pytest.mark.anyio
async def test_melder_list_answers() -> None:
    repository = Mock(BaseAnswerRepository)
    repository.find_by_melding.return_value = []

    repo_melding = Melding("melding text")
    repository.retrieve.return_value = repo_melding

    action: MeldingListQuestionsAnswersAction[Answer] = MeldingListQuestionsAnswersAction(repository)

    answers = await action(1)
    assert answers == []


@pytest.mark.anyio
async def test_submit_melding() -> None:
    repo_melding = Melding("text")
    state_machine = Mock(BaseMeldingStateMachine)
    repository = Mock(BaseMeldingRepository)
    token_verifier = AsyncMock(TokenVerifier)

    token_verifier.return_value = repo_melding
    token_invalidator = AsyncMock(BaseTokenInvalidator)

    confirmation_mailer = AsyncMock(BaseMeldingConfirmationMailer)

    action: MeldingSubmitAction[Melding] = MeldingSubmitAction(
        repository, state_machine, token_verifier, token_invalidator, confirmation_mailer
    )

    melding = await action(1, "token")
    assert melding == repo_melding

    state_machine.transition.assert_called_once_with(repo_melding, MeldingTransitions.SUBMIT)
    token_invalidator.assert_called_once_with(repo_melding)
    repository.save.assert_called_once_with(repo_melding)


@pytest.mark.anyio
async def test_add_asset_asset_type_not_found() -> None:
    asset_type_repository = Mock(BaseAssetTypeRepository)
    asset_type_repository.retrieve.return_value = None

    asset_repository = Mock(BaseAssetRepository)
    asset_repository.find_by_external_id_and_asset_type_id.return_value = None

    action: MeldingAddAssetAction[Melding, Asset, AssetType] = MeldingAddAssetAction(
        AsyncMock(TokenVerifier),
        Mock(BaseMeldingRepository),
        asset_repository,
        asset_type_repository,
        Mock(BaseAssetFactory),
        AsyncMock(RelationshipManager),
    )

    with pytest.raises(NotFoundException):
        await action(123, "external_id", 456, "token")


@pytest.mark.anyio
async def test_add_asset_asset_does_not_yet_exist() -> None:
    asset_repository = Mock(BaseAssetRepository)
    asset_repository.find_by_external_id_and_asset_type_id.return_value = None

    action: MeldingAddAssetAction[Melding, Asset, AssetType] = MeldingAddAssetAction(
        AsyncMock(TokenVerifier),
        Mock(BaseMeldingRepository),
        asset_repository,
        Mock(BaseAssetTypeRepository),
        Mock(BaseAssetFactory),
        AsyncMock(RelationshipManager),
    )

    melding = await action(123, "external_id", 456, "token")
    assert melding is not None


@pytest.mark.anyio
async def test_add_asset_asset_exists() -> None:
    action: MeldingAddAssetAction[Melding, Asset, AssetType] = MeldingAddAssetAction(
        AsyncMock(TokenVerifier),
        Mock(BaseMeldingRepository),
        Mock(BaseAssetRepository),
        Mock(BaseAssetTypeRepository),
        Mock(BaseAssetFactory),
        AsyncMock(RelationshipManager),
    )

    melding = await action(123, "external_id", 456, "token")
    assert melding is not None


@pytest.mark.anyio
async def test_delete_asset_asset_type_not_found() -> None:
    asset_type_repository = Mock(BaseAssetTypeRepository)
    asset_type_repository.retrieve.return_value = None

    asset_repository = Mock(BaseAssetRepository)
    asset_repository.retrieve.return_value = None

    action: MeldingDeleteAssetAction[Melding, Asset, AssetType] = MeldingDeleteAssetAction(
        AsyncMock(TokenVerifier),
        asset_repository,
        asset_type_repository,
    )

    with pytest.raises(NotFoundException):
        await action(123, 456, "token")


@pytest.mark.anyio
async def test_delete_asset_asset_does_not_exist() -> None:
    asset_repository = Mock(BaseAssetRepository)
    asset_repository.retrieve.return_value = None

    action: MeldingDeleteAssetAction[Melding, Asset, AssetType] = MeldingDeleteAssetAction(
        AsyncMock(TokenVerifier),
        asset_repository,
        Mock(BaseAssetTypeRepository),
    )

    with pytest.raises(NotFoundException):
        await action(123, 456, "token")


@pytest.mark.anyio
async def test_delete_asset_asset_does_not_belong_to_melding() -> None:
    melding = Melding(
        "text",
    )
    asset = Asset(
        external_id="external_id", type=AssetType(name="type", class_name="class_name", arguments={}), melding=melding
    )
    asset_repository = Mock(BaseAssetRepository)
    asset_repository.retrieve.return_value = asset

    token_verifier = AsyncMock(TokenVerifier)
    token_verifier.return_value = Melding("different melding")

    action: MeldingDeleteAssetAction[Melding, Asset, AssetType] = MeldingDeleteAssetAction(
        token_verifier,
        asset_repository,
        Mock(BaseAssetTypeRepository),
    )

    with pytest.raises(NotFoundException):
        await action(123, 456, "token")


@pytest.mark.anyio
async def test_delete_asset_asset_exists() -> None:
    melding = Melding(
        "text",
    )
    asset = Asset(
        external_id="external_id", type=AssetType(name="type", class_name="class_name", arguments={}), melding=melding
    )
    melding.assets = [asset]
    asset_repository = Mock(BaseAssetRepository)
    asset_repository.retrieve.return_value = asset
    token_verifier = AsyncMock(TokenVerifier)
    token_verifier.return_value = melding

    action: MeldingDeleteAssetAction[Melding, Asset, AssetType] = MeldingDeleteAssetAction(
        token_verifier,
        asset_repository,
        Mock(BaseAssetTypeRepository),
    )

    await action(123, 456, "token")

    asset_repository.delete.assert_awaited_once_with(456)
