import logging
from abc import ABCMeta, abstractmethod
from collections.abc import Sequence
from datetime import datetime, timedelta
from typing import Any, Generic, TypeVar, override

from meldingen_core.actions.base import BaseCreateAction, BaseCRUDAction, BaseListAction, BaseRetrieveAction
from meldingen_core.classification import ClassificationNotFoundException, Classifier
from meldingen_core.exceptions import NotFoundException
from meldingen_core.models import Answer, Melding
from meldingen_core.repositories import BaseAnswerRepository, BaseMeldingRepository, BaseRepository
from meldingen_core.statemachine import BaseMeldingStateMachine, MeldingTransitions
from meldingen_core.token import BaseTokenGenerator, TokenVerifier

log = logging.getLogger(__name__)

T = TypeVar("T", bound=Melding)
T_co = TypeVar("T_co", covariant=True, bound=Melding)


class MeldingCreateAction(BaseCreateAction[T, T_co]):
    """Action that stores a melding."""

    _classify: Classifier
    _state_machine: BaseMeldingStateMachine[T]
    _generate_token: BaseTokenGenerator
    _token_duration: timedelta

    def __init__(
        self,
        repository: BaseRepository[T, T_co],
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


class MeldingListAction(BaseListAction[T, T_co]):
    """Action that retrieves a list of meldingen."""


class MeldingRetrieveAction(BaseRetrieveAction[T, T_co]):
    """Action that retrieves a melding."""


class MeldingUpdateAction(BaseCRUDAction[T, T_co]):
    """Action that updates the melding and reclassifies it"""

    _verify_token: TokenVerifier[T, T_co]
    _classify: Classifier
    _state_machine: BaseMeldingStateMachine[T]

    def __init__(
        self,
        repository: BaseRepository[T, T_co],
        token_verifier: TokenVerifier[T, T_co],
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


class MeldingAddContactInfoAction(BaseCRUDAction[T, T_co]):
    """Action that adds contact information to a melding."""

    _verify_token: TokenVerifier[T, T_co]

    def __init__(
        self,
        repository: BaseMeldingRepository[T, T_co],
        token_verifier: TokenVerifier[T, T_co],
    ) -> None:
        super().__init__(repository)
        self._verify_token = token_verifier

    async def __call__(self, pk: int, phone: str | None, email: str | None, token: str) -> T:
        melding = await self._verify_token(pk, token)

        melding.phone = phone
        melding.email = email

        await self._repository.save(melding)

        return melding


class BaseStateTransitionAction(Generic[T, T_co], metaclass=ABCMeta):
    """
    This action covers transitions that do not require the melding's token to be verified.
    Typically these actions are performed by authenticated users.
    """

    _state_machine: BaseMeldingStateMachine[T]
    _repository: BaseMeldingRepository[T, T_co]

    def __init__(
        self,
        state_machine: BaseMeldingStateMachine[T],
        repository: BaseMeldingRepository[T, T_co],
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


class BaseMeldingFormStateTransitionAction(Generic[T, T_co], metaclass=ABCMeta):
    """
    This action covers transitions that require the melding's token to be verified.
    This is the case for unauthenticated state transitions where a user submits a melding.
    """

    _state_machine: BaseMeldingStateMachine[T]
    _repository: BaseMeldingRepository[T, T_co]
    _verify_token: TokenVerifier[T, T_co]

    def __init__(
        self,
        state_machine: BaseMeldingStateMachine[T],
        repository: BaseMeldingRepository[T, T_co],
        token_verifier: TokenVerifier[T, T_co],
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


class MeldingAnswerQuestionsAction(BaseMeldingFormStateTransitionAction[T, T_co]):
    @property
    def transition_name(self) -> str:
        return MeldingTransitions.ANSWER_QUESTIONS


class MeldingAddAttachmentsAction(BaseMeldingFormStateTransitionAction[T, T_co]):
    @property
    def transition_name(self) -> str:
        return MeldingTransitions.ADD_ATTACHMENTS


class MeldingSubmitLocationAction(BaseMeldingFormStateTransitionAction[T, T_co]):
    @property
    def transition_name(self) -> str:
        return MeldingTransitions.SUBMIT_LOCATION


class MeldingContactInfoAddedAction(BaseMeldingFormStateTransitionAction[T, T_co]):
    @property
    def transition_name(self) -> str:
        return MeldingTransitions.ADD_CONTACT_INFO


class MeldingProcessAction(BaseStateTransitionAction[T, T_co]):
    @property
    def transition_name(self) -> str:
        return MeldingTransitions.PROCESS


class MeldingCompleteAction(BaseStateTransitionAction[T, T_co]):
    @property
    def transition_name(self) -> str:
        return MeldingTransitions.COMPLETE


class MeldingListQuestionsAnswersAction(Generic[T, T_co]):
    _verify_token: TokenVerifier[T, T_co]
    _answer_repository: BaseAnswerRepository

    def __init__(
        self,
        token_verifier: TokenVerifier[T, T_co],
        answer_repository: BaseAnswerRepository,
    ) -> None:
        self._verify_token = token_verifier
        self._answer_repository = answer_repository

    async def __call__(self, melding_id: int, token: str) -> Sequence[Answer]:
        await self._verify_token(melding_id, token)

        return await self._answer_repository.find_by_melding(melding_id)
