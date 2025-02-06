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


class ClassificationCreateAction(BaseCreateAction[T]): ...


class ClassificationListAction(BaseListAction[T]): ...


class ClassificationRetrieveAction(BaseRetrieveAction[T]): ...


class ClassificationUpdateAction(BaseUpdateAction[T]): ...


class ClassificationDeleteAction(BaseDeleteAction[T]): ...
