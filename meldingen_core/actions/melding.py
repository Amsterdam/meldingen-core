import logging
from abc import ABCMeta, abstractmethod
from collections.abc import Sequence
from datetime import datetime, timedelta
from typing import Any, Generic, TypeVar, override

from meldingen_core import SortingDirection
from meldingen_core.actions.base import BaseCreateAction, BaseCRUDAction, BaseRetrieveAction
from meldingen_core.classification import ClassificationNotFoundException, Classifier
from meldingen_core.exceptions import NotFoundException
from meldingen_core.mail import BaseMeldingCompleteMailer, BaseMeldingConfirmationMailer
from meldingen_core.models import Answer, Melding
from meldingen_core.repositories import BaseAnswerRepository, BaseMeldingRepository, BaseRepository
from meldingen_core.statemachine import BaseMeldingStateMachine, MeldingTransitions
from meldingen_core.token import BaseTokenGenerator, BaseTokenInvalidator, TokenVerifier

log = logging.getLogger(__name__)

T = TypeVar("T", bound=Melding)


class MeldingCreateAction(BaseCreateAction[T]):
    """Action that stores a melding."""

    _classify: Classifier
    _state_machine: BaseMeldingStateMachine[T]
    _generate_token: BaseTokenGenerator
    _token_duration: timedelta

    def __init__(
        self,
        repository: BaseRepository[T],
        classifier: Classifier,
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
        area: str | None = None,
    ) -> Sequence[T]:
        return await self._repository.list_meldingen(
            limit=limit,
            offset=offset,
            sort_attribute_name=sort_attribute_name,
            sort_direction=sort_direction,
            area=area,
        )


class MeldingRetrieveAction(BaseRetrieveAction[T]):
    """Action that retrieves a melding."""


class MeldingUpdateAction(BaseCRUDAction[T]):
    """Action that updates the melding and reclassifies it"""

    _verify_token: TokenVerifier[T]
    _classify: Classifier
    _state_machine: BaseMeldingStateMachine[T]

    def __init__(
        self,
        repository: BaseRepository[T],
        token_verifier: TokenVerifier[T],
        classifier: Classifier,
        state_machine: BaseMeldingStateMachine[T],
    ) -> None:
        super().__init__(repository)
        self._verify_token = token_verifier
        self._classify = classifier
        self._state_machine = state_machine

    async def __call__(self, pk: int, values: dict[str, Any], token: str) -> T:
        melding = await self._verify_token(pk, token)

        for key, value in values.items():
            setattr(melding, key, value)

        classification = await self._classify(melding.text)
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
