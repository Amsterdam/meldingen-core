from abc import ABCMeta, abstractmethod
from enum import StrEnum
from typing import Generic, TypeVar

from meldingen_core.models import Melding

T = TypeVar("T", bound=Melding)


class MeldingStates(StrEnum):
    NEW = "new"
    CLASSIFIED = "classified"
    QUESTIONS_ANSWERED = "questions_answered"
    ATTACHMENTS_ADDED = "attachments_added"
    LOCATION_SUBMITTED = "location_submitted"
    PROCESSING = "processing"
    COMPLETED = "completed"


class MeldingTransitions(StrEnum):
    PROCESS = "process"
    CLASSIFY = "classify"
    ANSWER_QUESTIONS = "answer_questions"
    ADD_ATTACHMENTS = "add_attachments"
    SUBMIT_LOCATION = "submit_location"
    COMPLETE = "complete"


class BaseMeldingStateMachine(Generic[T], metaclass=ABCMeta):
    @abstractmethod
    async def transition(self, melding: T, transition_name: str) -> None: ...
