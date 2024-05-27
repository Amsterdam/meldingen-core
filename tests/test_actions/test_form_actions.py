from unittest.mock import Mock

from meldingen_core.actions.form import (
    FormCreateAction,
    FormDeleteAction,
    FormListAction,
    FormRetrieveAction,
    FormUpdateAction,
)
from meldingen_core.models import Form
from meldingen_core.repositories import BaseFormRepository


def test_can_instantiate_form_create_action() -> None:
    action = FormCreateAction(Mock(BaseFormRepository))
    assert isinstance(action, FormCreateAction)


def test_can_instantiate_form_list_action() -> None:
    action: FormListAction[Form, Form] = FormListAction(Mock(BaseFormRepository))
    assert isinstance(action, FormListAction)


def test_can_instantiate_form_retrieve_action() -> None:
    action: FormRetrieveAction[Form, Form] = FormRetrieveAction(Mock(BaseFormRepository))
    assert isinstance(action, FormRetrieveAction)


def test_can_instantiate_form_update_action() -> None:
    action: FormUpdateAction[Form, Form] = FormUpdateAction(Mock(BaseFormRepository))
    assert isinstance(action, FormUpdateAction)


def test_can_instantiate_form_delete_action() -> None:
    action = FormDeleteAction(Mock(BaseFormRepository))
    assert isinstance(action, FormDeleteAction)
