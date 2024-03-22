from typing import TypeVar

from meldingen_core.actions.base import (
    BaseCreateAction,
    BaseDeleteAction,
    BaseListAction,
    BaseRetrieveAction,
    BaseUpdateAction,
)
from meldingen_core.models import Classification

T = TypeVar("T", bound=Classification)
T_co = TypeVar("T_co", covariant=True, bound=Classification)


class ClassificationCreateAction(BaseCreateAction[Classification, Classification]): ...


class ClassificationListAction(BaseListAction[T, T_co]): ...


class ClassificationRetrieveAction(BaseRetrieveAction[T, T_co]): ...


class ClassificationUpdateAction(BaseUpdateAction[T, T_co]): ...


class ClassificationDeleteAction(BaseDeleteAction[Classification, Classification]): ...
