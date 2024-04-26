from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Generic, TypeVar, override

from meldingen_core.actions.base import (
    BaseCreateAction,
    BaseCRUDAction,
    BaseListAction,
    BaseRetrieveAction,
)
from meldingen_core.classification import Classifier
from meldingen_core.exceptions import InvalidTokenException, NotFoundException, TokenExpiredException
from meldingen_core.models import Melding
from meldingen_core.repositories import BaseMeldingRepository, BaseRepository
from meldingen_core.statemachine import BaseMeldingStateMachine, MeldingTransitions
from meldingen_core.token import BaseTokenGenerator

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

        classification = await self._classify(obj.text)
        obj.classification = classification

        await self._state_machine.transition(obj, MeldingTransitions.CLASSIFY)
        await self._repository.save(obj)


class MeldingListAction(BaseListAction[T, T_co]):
    """Action that retrieves a list of meldingen."""


class MeldingRetrieveAction(BaseRetrieveAction[T, T_co]):
    """Action that retrieves a melding."""


class MeldingUpdateAction(BaseCRUDAction[T, T_co]):
    async def __call__(self, pk: int, values: dict[str, Any], token: str) -> T:
        melding = await self._repository.retrieve(pk=pk)
        if melding is None:
            raise NotFoundException()

        if token != melding.token:
            raise InvalidTokenException()

        if melding.token_expires is not None and melding.token_expires < datetime.now():
            raise TokenExpiredException()

        for key, value in values.items():
            setattr(melding, key, value)

        await self._repository.save(melding)

        return melding


class BaseStateTransitionAction(Generic[T, T_co], metaclass=ABCMeta):
    _state_machine: BaseMeldingStateMachine[T]
    _repository: BaseMeldingRepository[T, T_co]

    def __init__(self, state_machine: BaseMeldingStateMachine[T], repository: BaseMeldingRepository[T, T_co]):
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


class MeldingProcessAction(BaseStateTransitionAction[T, T_co]):
    @property
    def transition_name(self) -> str:
        return MeldingTransitions.PROCESS


class MeldingCompleteAction(BaseStateTransitionAction[T, T_co]):
    @property
    def transition_name(self) -> str:
        return MeldingTransitions.COMPLETE
