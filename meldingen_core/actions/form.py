from typing import TypeVar

from meldingen_core.actions.base import (
    BaseCreateAction,
    BaseDeleteAction,
    BaseListAction,
    BaseRetrieveAction,
    BaseUpdateAction,
)
from meldingen_core.models import Form

T = TypeVar("T", bound=Form)
T_co = TypeVar("T_co", covariant=True, bound=Form)


class FormCreateAction(BaseCreateAction[Form, Form]): ...


class FormListAction(BaseListAction[T, T_co]): ...


class FormRetrieveAction(BaseRetrieveAction[T, T_co]): ...


class FormUpdateAction(BaseUpdateAction[T, T_co]): ...


class FormDeleteAction(BaseDeleteAction[Form, Form]): ...
