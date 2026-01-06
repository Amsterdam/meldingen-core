from abc import ABCMeta, abstractmethod
from enum import StrEnum, Enum
from typing import Generic, Sequence, TypeVar

from meldingen_core.models import Melding

T = TypeVar("T", bound=Melding)


class BaseMeldingState(str, Enum):
    pass


class MeldingFormStates(BaseMeldingState):
    NEW = "new"
    CLASSIFIED = "classified"
    QUESTIONS_ANSWERED = "questions_answered"
    ATTACHMENTS_ADDED = "attachments_added"
    LOCATION_SUBMITTED = "location_submitted"
    CONTACT_INFO_ADDED = "contact_info_added"


class MeldingBackofficeStates(BaseMeldingState):
    SUBMITTED = "submitted"
    AWAITING_PROCESSING = "awaiting_processing"
    PROCESSING = "processing"
    PLANNED = "planned"
    COMPLETED = "completed"
    CANCELED = "canceled"
    REOPENED = "reopened"
    REOPEN_REQUESTED = "reopen_requested"


class MeldingStates(BaseMeldingState):
    NEW = MeldingFormStates.NEW
    CLASSIFIED = MeldingFormStates.CLASSIFIED
    QUESTIONS_ANSWERED = MeldingFormStates.QUESTIONS_ANSWERED
    ATTACHMENTS_ADDED = MeldingFormStates.ATTACHMENTS_ADDED
    LOCATION_SUBMITTED = MeldingFormStates.LOCATION_SUBMITTED
    CONTACT_INFO_ADDED = MeldingFormStates.CONTACT_INFO_ADDED
    SUBMITTED = MeldingBackofficeStates.SUBMITTED
    AWAITING_PROCESSING = MeldingBackofficeStates.AWAITING_PROCESSING
    PROCESSING = MeldingBackofficeStates.PROCESSING
    PLANNED = MeldingBackofficeStates.PLANNED
    COMPLETED = MeldingBackofficeStates.COMPLETED
    CANCELED = MeldingBackofficeStates.CANCELED
    REOPENED = MeldingBackofficeStates.REOPENED
    REOPEN_REQUESTED = MeldingBackofficeStates.REOPEN_REQUESTED


class MeldingTransitions(StrEnum):
    CLASSIFY = "classify"
    ANSWER_QUESTIONS = "answer_questions"
    ADD_ATTACHMENTS = "add_attachments"
    SUBMIT_LOCATION = "submit_location"
    ADD_CONTACT_INFO = "add_contact_info"
    SUBMIT = "submit"
    REQUEST_PROCESSING = "request_processing"
    PLAN = "plan"
    CANCEL = "cancel"
    REQUEST_REOPEN = "request_reopen"
    REOPEN = "reopen"
    PROCESS = "process"
    COMPLETE = "complete"


class BaseMeldingStateMachine(Generic[T], metaclass=ABCMeta):
    @abstractmethod
    async def transition(self, melding: T, transition_name: str) -> None: ...


def get_all_backoffice_states() -> Sequence[MeldingBackofficeStates]:
    return [e for e in MeldingBackofficeStates]
