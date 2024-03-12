from abc import ABCMeta, abstractmethod
from typing import TypeVar

from meldingen_core.actions.base import BaseCreateAction, BaseListAction, BaseRetrieveAction
from meldingen_core.exceptions import NotFoundException
from meldingen_core.models import Melding
from meldingen_core.repositories import BaseMeldingRepository
from meldingen_core.statemachine import BaseMeldingStateMachine, MeldingTransitions

T = TypeVar("T", bound=Melding)
T_co = TypeVar("T_co", covariant=True, bound=Melding)


class MeldingCreateAction(BaseCreateAction[Melding, Melding]):
    """Action that stores a melding."""


class MeldingListAction(BaseListAction[T, T_co]):
    """Action that retrieves a list of meldingen."""


class MeldingRetrieveAction(BaseRetrieveAction[T, T_co]):
    """Action that retrieves a melding."""


class BaseStateTransitionAction(metaclass=ABCMeta):
    _state_machine: BaseMeldingStateMachine
    _repository: BaseMeldingRepository

    def __init__(self, state_machine: BaseMeldingStateMachine, repository: BaseMeldingRepository):
        self._state_machine = state_machine
        self._repository = repository

    @abstractmethod
    async def __call__(self, melding_id: int) -> Melding:
        ...


class MeldingProcessAction(BaseStateTransitionAction):
    async def __call__(self, melding_id: int) -> Melding:
        melding = await self._repository.retrieve(melding_id)
        if melding is None:
            raise NotFoundException()

        await self._state_machine.transition(melding, MeldingTransitions.PROCESS)
        await self._repository.save(melding)

        return melding
