from abc import ABCMeta, abstractmethod
from enum import StrEnum
from typing import Generic, TypeVar

from meldingen_core.models import Melding

T = TypeVar("T", bound=Melding)


class MeldingFormStates(StrEnum):
    NEW = "new"
    CLASSIFIED = "classified"
    QUESTIONS_ANSWERED = "questions_answered"
    ATTACHMENTS_ADDED = "attachments_added"
    LOCATION_SUBMITTED = "location_submitted"
    CONTACT_INFO_ADDED = "contact_info_added"


class MeldingBackofficeStates(StrEnum):
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    COMPLETED = "completed"


class MeldingStates(StrEnum):
    NEW = MeldingFormStates.NEW
    CLASSIFIED = MeldingFormStates.CLASSIFIED
    QUESTIONS_ANSWERED = MeldingFormStates.QUESTIONS_ANSWERED
    ATTACHMENTS_ADDED = MeldingFormStates.ATTACHMENTS_ADDED
    LOCATION_SUBMITTED = MeldingFormStates.LOCATION_SUBMITTED
    CONTACT_INFO_ADDED = MeldingFormStates.CONTACT_INFO_ADDED
    SUBMITTED = MeldingBackofficeStates.SUBMITTED
    PROCESSING = MeldingBackofficeStates.PROCESSING
    COMPLETED = MeldingBackofficeStates.COMPLETED


class MeldingTransitions(StrEnum):
    CLASSIFY = "classify"
    ANSWER_QUESTIONS = "answer_questions"
    ADD_ATTACHMENTS = "add_attachments"
    SUBMIT_LOCATION = "submit_location"
    ADD_CONTACT_INFO = "add_contact_info"
    SUBMIT = "submit"
    PROCESS = "process"
    COMPLETE = "complete"


class BaseMeldingStateMachine(Generic[T], metaclass=ABCMeta):
    @abstractmethod
    async def transition(self, melding: T, transition_name: str) -> None: ...
