from unittest.mock import Mock

from meldingen_core.actions.melding import MeldingCreateAction, MeldingListAction, MeldingRetrieveAction
from meldingen_core.models import Melding
from meldingen_core.repositories import BaseMeldingRepository


def test_can_instantiate_melding_create_action() -> None:
    action = MeldingCreateAction(Mock(BaseMeldingRepository))
    assert isinstance(action, MeldingCreateAction)


def test_can_instantiate_melding_list_action() -> None:
    action: MeldingListAction[Melding, Melding] = MeldingListAction(Mock(BaseMeldingRepository))
    assert isinstance(action, MeldingListAction)


def test_can_instantie_melding_retrieve_action() -> None:
    action: MeldingRetrieveAction[Melding, Melding] = MeldingRetrieveAction(Mock(BaseMeldingRepository))
    assert isinstance(action, MeldingRetrieveAction)
