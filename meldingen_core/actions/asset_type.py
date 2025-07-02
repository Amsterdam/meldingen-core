from typing import TypeVar

from meldingen_core.actions.base import (
    BaseCreateAction,
    BaseDeleteAction,
    BaseListAction,
    BaseRetrieveAction,
    BaseUpdateAction,
)
from meldingen_core.models import AssetType

AT = TypeVar("AT", bound=AssetType)


class AssetTypeCreateAction(BaseCreateAction[AT]): ...


class AssetTypeRetrieveAction(BaseRetrieveAction[AT]): ...


class AssetTypeListAction(BaseListAction[AT]): ...


class AssetTypeUpdateAction(BaseUpdateAction[AT]): ...


class AssetTypeDeleteAction(BaseDeleteAction[AT]): ...
