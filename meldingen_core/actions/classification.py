from meldingen_core.actions.base import (
    BaseCreateAction,
    BaseDeleteAction,
    BaseListAction,
    BaseRetrieveAction,
    BaseUpdateAction,
)
from meldingen_core.models import Classification


class ClassificationCreateAction(BaseCreateAction[Classification, Classification]):
    ...


class ClassificationListAction(BaseListAction[Classification, Classification]):
    ...


class ClassificationRetrieveAction(BaseRetrieveAction[Classification, Classification]):
    ...


class ClassificationUpdateAction(BaseUpdateAction[Classification, Classification]):
    ...


class ClassificationDeleteAction(BaseDeleteAction[Classification, Classification]):
    ...
