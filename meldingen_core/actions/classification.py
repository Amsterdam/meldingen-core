from typing import Any, Generic, TypeVar, override

from meldingen_core.actions.base import (
    BaseCreateAction,
    BaseDeleteAction,
    BaseListAction,
    BaseRetrieveAction,
    BaseUpdateAction,
)
from meldingen_core.exceptions import NotFoundException
from meldingen_core.models import AssetType, Classification
from meldingen_core.repositories import BaseAssetTypeRepository, BaseRepository

T = TypeVar("T", bound=Classification)
AT = TypeVar("AT", bound=AssetType)


class ClassificationCreateAction(Generic[T, AT], BaseCreateAction[T]):
    _asset_type_repository: BaseAssetTypeRepository[AT]

    @override
    def __init__(self, repository: BaseRepository[T], asset_type_repository: BaseAssetTypeRepository[AT]) -> None:
        super().__init__(repository)
        self._asset_type_repository = asset_type_repository

    @override
    async def __call__(self, obj: T, asset_type_id: int | None = None) -> None:
        if asset_type_id is not None:
            asset_type = await self._asset_type_repository.retrieve(asset_type_id)
            if asset_type is None:
                raise NotFoundException(f"Failed to find asset type with id '{asset_type_id}'")

            obj.asset_type = asset_type

        await super().__call__(obj)


class ClassificationListAction(BaseListAction[T]): ...


class ClassificationRetrieveAction(BaseRetrieveAction[T]): ...


class ClassificationUpdateAction(Generic[T, AT], BaseUpdateAction[T]):
    _asset_type_repository: BaseAssetTypeRepository[AT]

    @override
    def __init__(self, repository: BaseRepository[T], asset_type_repository: BaseAssetTypeRepository[AT]) -> None:
        super().__init__(repository)
        self._asset_type_repository = asset_type_repository

    @override
    async def __call__(self, pk: int, values: dict[str, Any]) -> T:
        asset_type_id = values.get("asset_type")
        if asset_type_id is not None:
            asset_type = await self._asset_type_repository.retrieve(asset_type_id)
            if asset_type is None:
                raise NotFoundException(f"Failed to find asset type with id '{asset_type_id}'")

            values["asset_type"] = asset_type

        return await super().__call__(pk, values)


class ClassificationDeleteAction(BaseDeleteAction[T]): ...
