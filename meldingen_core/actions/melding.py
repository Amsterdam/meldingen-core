from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar, override

from meldingen_core.actions.base import BaseCreateAction, BaseListAction, BaseRetrieveAction
from meldingen_core.classification import Classifier
from meldingen_core.exceptions import NotFoundException
from meldingen_core.models import Melding
from meldingen_core.repositories import BaseMeldingRepository, BaseRepository
from meldingen_core.statemachine import BaseMeldingStateMachine, MeldingTransitions

T = TypeVar("T", bound=Melding)
T_co = TypeVar("T_co", covariant=True, bound=Melding)


class MeldingCreateAction(BaseCreateAction[T, T_co]):
    """Action that stores a melding."""

    _classify: Classifier
    _state_machine: BaseMeldingStateMachine[T]

    def __init__(
        self,
        repository: BaseRepository[T, T_co],
        classifier: Classifier,
        state_machine: BaseMeldingStateMachine[T],
    ):
        super().__init__(repository)
        self._classify = classifier
        self._state_machine = state_machine

    @override
    async def __call__(self, obj: T) -> None:
        await super().__call__(obj)

        classification = await self._classify(obj.text)
        obj.classification = classification

        await self._state_machine.transition(obj, MeldingTransitions.CLASSIFY)
        await self._repository.save(obj)


class MeldingListAction(BaseListAction[T, T_co]):
    """Action that retrieves a list of meldingen."""


class MeldingRetrieveAction(BaseRetrieveAction[T, T_co]):
    """Action that retrieves a melding."""


class BaseStateTransitionAction(Generic[T, T_co], metaclass=ABCMeta):
    _state_machine: BaseMeldingStateMachine[T]
    _repository: BaseMeldingRepository[T, T_co]

    def __init__(self, state_machine: BaseMeldingStateMachine[T], repository: BaseMeldingRepository[T, T_co]):
        self._state_machine = state_machine
        self._repository = repository

    @property
    @abstractmethod
    def transition_name(self) -> str:
        ...

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
