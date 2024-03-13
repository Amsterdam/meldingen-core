from abc import ABCMeta, abstractmethod
from enum import StrEnum
from typing import Generic, TypeVar

from meldingen_core.models import Melding

T = TypeVar("T", bound=Melding)


class MeldingStates(StrEnum):
    NEW = "new"
    PROCESSING = "processing"
    COMPLETED = "completed"


class MeldingTransitions(StrEnum):
    PROCESS = "process"
    COMPLETE = "complete"


class BaseMeldingStateMachine(Generic[T], metaclass=ABCMeta):
    @abstractmethod
    async def transition(self, melding: T, transition_name: str) -> None:
        ...
