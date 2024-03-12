from abc import ABCMeta, abstractmethod
from enum import StrEnum

from meldingen_core.models import Melding


class MeldingStates(StrEnum):
    NEW = "new"
    PROCESSING = "processing"
    COMPLETED = "completed"


class MeldingTransitions(StrEnum):
    PROCESS = "process"
    COMPLETE = "complete"


class MeldingStateMachine(metaclass=ABCMeta):
    @abstractmethod
    async def transition(self, melding: Melding, transition_name: str) -> None:
        ...
