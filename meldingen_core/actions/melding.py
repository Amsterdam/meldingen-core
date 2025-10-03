import logging
from abc import ABCMeta, abstractmethod
from collections.abc import Sequence
from datetime import datetime, timedelta
from typing import Any, Generic, TypeVar, cast, override

from meldingen_core import SortingDirection
from meldingen_core.actions.base import BaseCreateAction, BaseCRUDAction, BaseRetrieveAction
from meldingen_core.classification import ClassificationNotFoundException, Classifier
from meldingen_core.exceptions import NotFoundException
from meldingen_core.factories import BaseAssetFactory
from meldingen_core.filters import MeldingListFilters
from meldingen_core.mail import BaseMeldingCompleteMailer, BaseMeldingConfirmationMailer
from meldingen_core.models import Answer, Asset, AssetType, Classification, Melding
from meldingen_core.reclassification import BaseReclassification
from meldingen_core.repositories import (
    BaseAnswerRepository,
    BaseAssetRepository,
    BaseAssetTypeRepository,
    BaseMeldingRepository,
    BaseRepository,
)
from meldingen_core.statemachine import BaseMeldingStateMachine, MeldingTransitions
from meldingen_core.token import BaseTokenGenerator, BaseTokenInvalidator, TokenVerifier

log = logging.getLogger(__name__)

C = TypeVar("C", bound=Classification)
T = TypeVar("T", bound=Melding)
AS = TypeVar("AS", bound=Asset)
AT = TypeVar("AT", bound=AssetType)


class MeldingCreateAction(Generic[T, C], BaseCreateAction[T]):
    """Action that stores a melding."""

    _classify: Classifier[C]
    _state_machine: BaseMeldingStateMachine[T]
    _generate_token: BaseTokenGenerator
    _token_duration: timedelta

    def __init__(
        self,
        repository: BaseRepository[T],
        classifier: Classifier[C],
        state_machine: BaseMeldingStateMachine[T],
        token_generator: BaseTokenGenerator,
        token_duration: timedelta,
    ):
        super().__init__(repository)
        self._classify = classifier
        self._state_machine = state_machine
        self._generate_token = token_generator
        self._token_duration = token_duration

    @override
    async def __call__(self, obj: T) -> None:
        await super().__call__(obj)

        obj.token = await self._generate_token()
        obj.token_expires = datetime.now() + self._token_duration

        try:
            classification = await self._classify(obj.text)
            obj.classification = classification
            await self._state_machine.transition(obj, MeldingTransitions.CLASSIFY)
        except ClassificationNotFoundException:
            log.error("Classifier failed to find classification!")

        await self._repository.save(obj)


class MeldingListAction(Generic[T]):
    """Action that retrieves a list of meldingen."""

    _repository: BaseMeldingRepository[T]

    def __init__(self, repository: BaseMeldingRepository[T]) -> None:
        self._repository = repository

    async def __call__(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        sort_attribute_name: str | None = None,
        sort_direction: SortingDirection | None = None,
        filters: MeldingListFilters | None = None,
    ) -> Sequence[T]:
        return await self._repository.list_meldingen(
            limit=limit,
            offset=offset,
            sort_attribute_name=sort_attribute_name,
            sort_direction=sort_direction,
            filters=filters,
        )


class MeldingRetrieveAction(BaseRetrieveAction[T]):
    """Action that retrieves a melding."""


class MeldingUpdateAction(Generic[T, C], BaseCRUDAction[T]):
    """Action that updates the melding and reclassifies it"""

    _verify_token: TokenVerifier[T]
    _classify: Classifier[C]
    _state_machine: BaseMeldingStateMachine[T]
    _reclassifier: BaseReclassification[T, C]

    def __init__(
        self,
        repository: BaseRepository[T],
        token_verifier: TokenVerifier[T],
        classifier: Classifier[C],
        state_machine: BaseMeldingStateMachine[T],
        reclassifier: BaseReclassification[T, C],
    ) -> None:
        super().__init__(repository)
        self._verify_token = token_verifier
        self._classify = classifier
        self._state_machine = state_machine
        self._reclassifier = reclassifier

    async def __call__(self, pk: int, values: dict[str, Any], token: str) -> T:
        melding = await self._verify_token(pk, token)
        old_classification: C = cast(C, melding.classification)

        for key, value in values.items():
            setattr(melding, key, value)

        try:
            classification = await self._classify(melding.text)
        except ClassificationNotFoundException:
            log.error("Classifier failed to find classification!")
            classification = None

        await self._reclassifier(melding, old_classification, classification)
        melding.classification = classification

        await self._state_machine.transition(melding, MeldingTransitions.CLASSIFY)
        await self._repository.save(melding)

        return melding


class MeldingAddContactInfoAction(BaseCRUDAction[T]):
    """Action that adds contact information to a melding."""

    _verify_token: TokenVerifier[T]

    def __init__(
        self,
        repository: BaseMeldingRepository[T],
        token_verifier: TokenVerifier[T],
    ) -> None:
        super().__init__(repository)
        self._verify_token = token_verifier

    async def __call__(self, pk: int, phone: str | None, email: str | None, token: str) -> T:
        melding = await self._verify_token(pk, token)

        melding.phone = phone
        melding.email = email

        await self._repository.save(melding)

        return melding


class BaseStateTransitionAction(Generic[T], metaclass=ABCMeta):
    """
    This action covers transitions that do not require the melding's token to be verified.
    Typically these actions are performed by authenticated users.
    """

    _state_machine: BaseMeldingStateMachine[T]
    _repository: BaseMeldingRepository[T]

    def __init__(
        self,
        state_machine: BaseMeldingStateMachine[T],
        repository: BaseMeldingRepository[T],
    ):
        self._state_machine = state_machine
        self._repository = repository

    @property
    @abstractmethod
    def transition_name(self) -> str: ...

    async def __call__(self, melding_id: int) -> T:
        melding = await self._repository.retrieve(melding_id)
        if melding is None:
            raise NotFoundException()

        await self._state_machine.transition(melding, self.transition_name)
        await self._repository.save(melding)

        return melding


class BaseMeldingFormStateTransitionAction(Generic[T], metaclass=ABCMeta):
    """
    This action covers transitions that require the melding's token to be verified.
    This is the case for unauthenticated state transitions where a user submits a melding.
    """

    _state_machine: BaseMeldingStateMachine[T]
    _repository: BaseMeldingRepository[T]
    _verify_token: TokenVerifier[T]

    def __init__(
        self,
        state_machine: BaseMeldingStateMachine[T],
        repository: BaseMeldingRepository[T],
        token_verifier: TokenVerifier[T],
    ):
        self._state_machine = state_machine
        self._repository = repository
        self._verify_token = token_verifier

    @property
    @abstractmethod
    def transition_name(self) -> str: ...

    async def __call__(self, melding_id: int, token: str) -> T:
        melding = await self._verify_token(melding_id, token)

        await self._state_machine.transition(melding, self.transition_name)
        await self._repository.save(melding)

        return melding


class MeldingAnswerQuestionsAction(BaseMeldingFormStateTransitionAction[T]):
    @property
    def transition_name(self) -> str:
        return MeldingTransitions.ANSWER_QUESTIONS


class MeldingAddAttachmentsAction(BaseMeldingFormStateTransitionAction[T]):
    @property
    def transition_name(self) -> str:
        return MeldingTransitions.ADD_ATTACHMENTS


class MeldingSubmitLocationAction(BaseMeldingFormStateTransitionAction[T]):
    @property
    def transition_name(self) -> str:
        return MeldingTransitions.SUBMIT_LOCATION


class MeldingContactInfoAddedAction(BaseMeldingFormStateTransitionAction[T]):
    @property
    def transition_name(self) -> str:
        return MeldingTransitions.ADD_CONTACT_INFO


class MeldingProcessAction(BaseStateTransitionAction[T]):
    @property
    def transition_name(self) -> str:
        return MeldingTransitions.PROCESS


class MeldingCompleteAction(Generic[T]):
    _state_machine: BaseMeldingStateMachine[T]
    _repository: BaseMeldingRepository[T]
    _mailer: BaseMeldingCompleteMailer[T]

    def __init__(
        self,
        state_machine: BaseMeldingStateMachine[T],
        repository: BaseMeldingRepository[T],
        mailer: BaseMeldingCompleteMailer[T],
    ):
        self._state_machine = state_machine
        self._repository = repository
        self._mailer = mailer

    async def __call__(self, melding_id: int, mail_text: str | None = None) -> T:
        melding = await self._repository.retrieve(melding_id)
        if melding is None:
            raise NotFoundException()

        await self._state_machine.transition(melding, MeldingTransitions.COMPLETE)
        await self._repository.save(melding)

        if mail_text is not None:
            await self._mailer.__call__(melding, mail_text)

        return melding


A = TypeVar("A", bound=Answer)


class MelderMeldingListQuestionsAnswersAction(Generic[T, A]):
    _verify_token: TokenVerifier[T]
    _answer_repository: BaseAnswerRepository[A]

    def __init__(
        self,
        token_verifier: TokenVerifier[T],
        answer_repository: BaseAnswerRepository[A],
    ) -> None:
        self._verify_token = token_verifier
        self._answer_repository = answer_repository

    async def __call__(self, melding_id: int, token: str) -> Sequence[A]:
        await self._verify_token(melding_id, token)

        return await self._answer_repository.find_by_melding(melding_id)


class MeldingListQuestionsAnswersAction(Generic[A]):
    _answer_repository: BaseAnswerRepository[A]

    def __init__(
        self,
        answer_repository: BaseAnswerRepository[A],
    ) -> None:
        self._answer_repository = answer_repository

    async def __call__(self, melding_id: int) -> Sequence[A]:
        return await self._answer_repository.find_by_melding(melding_id)


class MeldingSubmitAction(BaseCRUDAction[T]):
    _repository: BaseMeldingRepository[T]
    _state_machine: BaseMeldingStateMachine[T]
    _verify_token: TokenVerifier[T]
    _invalidate_token: BaseTokenInvalidator[T]
    _send_mail: BaseMeldingConfirmationMailer[T]

    def __init__(
        self,
        repository: BaseMeldingRepository[T],
        state_machine: BaseMeldingStateMachine[T],
        token_verifier: TokenVerifier[T],
        token_invalidator: BaseTokenInvalidator[T],
        confirmation_mailer: BaseMeldingConfirmationMailer[T],
    ) -> None:
        self._repository = repository
        self._state_machine = state_machine
        self._verify_token = token_verifier
        self._invalidate_token = token_invalidator
        self._send_mail = confirmation_mailer

    async def __call__(
        self,
        melding_id: int,
        token: str,
    ) -> T:
        melding = await self._verify_token(melding_id, token)
        await self._state_machine.transition(melding, self.transition_name)
        await self._invalidate_token(melding)
        await self._repository.save(melding)
        await self._send_mail(melding)

        return melding

    @property
    def transition_name(self) -> str:
        return MeldingTransitions.SUBMIT


class MeldingAddAssetAction(Generic[T, AS, AT]):
    _verify_token: TokenVerifier[T]
    _melding_repository: BaseMeldingRepository[T]
    _asset_repository: BaseAssetRepository[AS]
    _asset_type_repository: BaseAssetTypeRepository[AT]
    _create_asset: BaseAssetFactory[AS, AT, T]

    def __init__(
        self,
        token_verifier: TokenVerifier[T],
        melding_repository: BaseMeldingRepository[T],
        asset_repository: BaseAssetRepository[AS],
        asset_type_repository: BaseAssetTypeRepository[AT],
        asset_factory: BaseAssetFactory[AS, AT, T],
    ):
        self._verify_token = token_verifier
        self._melding_repository = melding_repository
        self._asset_repository = asset_repository
        self._asset_type_repository = asset_type_repository
        self._create_asset = asset_factory

    async def __call__(self, melding_id: int, external_asset_id: str, asset_type_id: int, token: str) -> T:
        melding = await self._verify_token(melding_id, token)

        asset = await self._asset_repository.find_by_external_id_and_asset_type_id(external_asset_id, asset_type_id)
        if asset is None:
            asset_type = await self._asset_type_repository.retrieve(asset_type_id)
            if asset_type is None:
                raise NotFoundException(f"Failed to find asset type with id {asset_type_id}")

            asset = self._create_asset(external_asset_id, asset_type, melding)
            await self._asset_repository.save(asset)

        return melding


class MeldingDeleteAssetAction(Generic[T, AS, AT]):
    _verify_token: TokenVerifier[T]
    _asset_repository: BaseAssetRepository[AS]
    _asset_type_repository: BaseAssetTypeRepository[AT]

    def __init__(
        self,
        token_verifier: TokenVerifier[T],
        asset_repository: BaseAssetRepository[AS],
        asset_type_repository: BaseAssetTypeRepository[AT],
    ):
        self._verify_token = token_verifier
        self._asset_repository = asset_repository
        self._asset_type_repository = asset_type_repository

    async def __call__(self, melding_id: int, asset_id: int, token: str) -> None:
        melding = await self._verify_token(melding_id, token)
        asset = await self._asset_repository.retrieve(asset_id)

        if asset is None:
            raise NotFoundException(f"Failed to find asset with id {asset_id}")

        if asset.melding is not melding:
            raise NotFoundException(f"Melding with id {melding_id} does not have asset with id {asset_id} associated")

        melding.assets.remove(asset)

        await self._asset_repository.delete(asset_id)
