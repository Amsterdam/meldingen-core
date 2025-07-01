from typing import TypeVar

from meldingen_core.actions.base import BaseCreateAction, BaseDeleteAction, BaseRetrieveAction, BaseUpdateAction
from meldingen_core.models import AssetType

AT = TypeVar("AT", bound=AssetType)


class AssetTypeCreateAction(BaseCreateAction[AT]): ...


class AssetTypeRetrieveAction(BaseRetrieveAction[AT]): ...


class AssetTypeUpdateAction(BaseUpdateAction[AT]): ...


class AssetTypeDeleteAction(BaseDeleteAction[AT]): ...
