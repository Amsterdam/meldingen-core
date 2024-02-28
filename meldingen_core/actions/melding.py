from typing import TypeVar

from meldingen_core.actions.base import BaseCreateAction, BaseListAction, BaseRetrieveAction
from meldingen_core.models import Melding

T = TypeVar("T", bound=Melding)
T_co = TypeVar("T_co", covariant=True, bound=Melding)


class MeldingCreateAction(BaseCreateAction[Melding, Melding]):
    """Action that stores a melding."""


class MeldingListAction(BaseListAction[T, T_co]):
    """Action that retrieves a list of meldingen."""


class MeldingRetrieveAction(BaseRetrieveAction[T, T_co]):
    """Action that retrieves a melding."""
