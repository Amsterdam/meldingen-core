from unittest.mock import Mock

from meldingen_core.actions.classification import (
    ClassificationCreateAction,
    ClassificationDeleteAction,
    ClassificationListAction,
    ClassificationRetrieveAction,
    ClassificationUpdateAction,
)
from meldingen_core.models import Classification
from meldingen_core.repositories import BaseClassificationRepository


def test_can_instantiate_create_action() -> None:
    action: ClassificationCreateAction[Classification] = ClassificationCreateAction(Mock(BaseClassificationRepository))
    assert isinstance(action, ClassificationCreateAction)


def test_can_instantiate_retrieve_action() -> None:
    action: ClassificationRetrieveAction[Classification] = ClassificationRetrieveAction(
        Mock(BaseClassificationRepository)
    )
    assert isinstance(action, ClassificationRetrieveAction)


def test_can_instantiate_list_action() -> None:
    action: ClassificationListAction[Classification] = ClassificationListAction(Mock(BaseClassificationRepository))
    assert isinstance(action, ClassificationListAction)


def test_can_instantiate_update_action() -> None:
    action: ClassificationUpdateAction[Classification] = ClassificationUpdateAction(Mock(BaseClassificationRepository))
    assert isinstance(action, ClassificationUpdateAction)


def test_can_instantiate_delete_action() -> None:
    action: ClassificationDeleteAction[Classification] = ClassificationDeleteAction(Mock(BaseClassificationRepository))
    assert isinstance(action, ClassificationDeleteAction)
