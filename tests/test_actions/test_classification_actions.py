from unittest.mock import Mock

import pytest

from meldingen_core.actions.classification import (
    ClassificationCreateAction,
    ClassificationDeleteAction,
    ClassificationListAction,
    ClassificationRetrieveAction,
    ClassificationUpdateAction,
)
from meldingen_core.exceptions import NotFoundException
from meldingen_core.models import AssetType, Classification
from meldingen_core.repositories import BaseAssetTypeRepository, BaseClassificationRepository


class TestClassificationCreateAction:
    def test_can_instantiate_create_action(self) -> None:
        action: ClassificationCreateAction[Classification, AssetType] = ClassificationCreateAction(
            Mock(BaseClassificationRepository), Mock(BaseAssetTypeRepository)
        )
        assert isinstance(action, ClassificationCreateAction)

    @pytest.mark.anyio
    async def test_raises_exception_when_asset_type_not_found(self) -> None:
        asset_type_repository = Mock(BaseAssetTypeRepository)
        asset_type_repository.retrieve.return_value = None

        action: ClassificationCreateAction[Classification, AssetType] = ClassificationCreateAction(
            Mock(BaseClassificationRepository), asset_type_repository
        )

        with pytest.raises(NotFoundException):
            await action(Classification("name"), 123)

    @pytest.mark.anyio
    async def test_can_create_classification_with_asset_type(self) -> None:
        action: ClassificationCreateAction[Classification, AssetType] = ClassificationCreateAction(
            Mock(BaseClassificationRepository), Mock(BaseAssetTypeRepository)
        )

        await action(Classification("name"), 123)


def test_can_instantiate_retrieve_action() -> None:
    action: ClassificationRetrieveAction[Classification] = ClassificationRetrieveAction(
        Mock(BaseClassificationRepository)
    )
    assert isinstance(action, ClassificationRetrieveAction)


def test_can_instantiate_list_action() -> None:
    action: ClassificationListAction[Classification] = ClassificationListAction(Mock(BaseClassificationRepository))
    assert isinstance(action, ClassificationListAction)


class TestClassificationUpdateAction:
    def test_can_instantiate_update_action(self) -> None:
        action: ClassificationUpdateAction[Classification, AssetType] = ClassificationUpdateAction(
            Mock(BaseClassificationRepository), Mock(BaseAssetTypeRepository)
        )
        assert isinstance(action, ClassificationUpdateAction)

    @pytest.mark.anyio
    async def test_raises_exception_when_asset_type_not_found(self) -> None:
        asset_type_repository = Mock(BaseAssetTypeRepository)
        asset_type_repository.retrieve.return_value = None

        action: ClassificationUpdateAction[Classification, AssetType] = ClassificationUpdateAction(
            Mock(BaseClassificationRepository), asset_type_repository
        )

        with pytest.raises(NotFoundException):
            await action(123, {"asset_type": 456})

    @pytest.mark.anyio
    async def test_can_update_classification_with_asset_type(self) -> None:
        action: ClassificationUpdateAction[Classification, AssetType] = ClassificationUpdateAction(
            Mock(BaseClassificationRepository), Mock(BaseAssetTypeRepository)
        )

        classification = await action(123, {"asset_type": 456})
        assert classification is not None


def test_can_instantiate_delete_action() -> None:
    action: ClassificationDeleteAction[Classification] = ClassificationDeleteAction(Mock(BaseClassificationRepository))
    assert isinstance(action, ClassificationDeleteAction)
