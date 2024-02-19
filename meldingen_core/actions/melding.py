from meldingen_core.actions.base import BaseCreateAction, BaseListAction, BaseRetrieveAction
from meldingen_core.models import Melding


class MeldingCreateAction(BaseCreateAction[Melding, Melding]):
    """Action that stores a melding."""


class MeldingListAction(BaseListAction[Melding, Melding]):
    """Action that retrieves a list of meldingen."""


class MeldingRetrieveAction(BaseRetrieveAction[Melding, Melding]):
    """Action that retrieves a melding."""
