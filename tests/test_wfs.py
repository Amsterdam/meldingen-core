from typing import AsyncIterator

import pytest

from meldingen_core.models import AssetType
from meldingen_core.wfs import BaseWfsProvider, InvalidWfsProviderException, WfsProviderFactory


class InvalidWfsProvider:
    def __init__(self, arg1: int, arg2: str) -> None: ...


class ValidWfsProvider(BaseWfsProvider):
    async def __call__(  # type: ignore
        self,
        type_names: str,
        count: int = 1000,
        srs_name: str = "urn:ogc:def:crs:EPSG::4326",
        output_format: str = "application/json",
        filter: str | None = None,
    ) -> tuple[AsyncIterator[bytes], str]: ...


def test_wfs_provider_factory_raises_when_class_name_invalid() -> None:
    factory = WfsProviderFactory()

    with pytest.raises(InvalidWfsProviderException) as exception_info:
        factory(AssetType("asset_type_name", "invalid_value", {}))

    assert str(exception_info.value) == "class_name 'invalid_value' does not contain full path to class"


def test_wfs_provider_factory_raises_when_module_name_invalid() -> None:
    factory = WfsProviderFactory()

    with pytest.raises(InvalidWfsProviderException) as exception_info:
        factory(AssetType("asset_type_name", "invalid_module_name.Test", {}))

    assert str(exception_info.value) == "Failed to find module 'invalid_module_name'"


def test_wfs_provider_factory_raises_when_class_does_not_exist() -> None:
    factory = WfsProviderFactory()

    with pytest.raises(InvalidWfsProviderException) as exception_info:
        factory(AssetType("asset_type_name", "tests.test_wfs.Test", {}))

    assert str(exception_info.value) == "Failed to find class 'Test' in module 'tests.test_wfs'"


def test_wfs_provider_factory_raises_when_class_can_not_be_instantiated() -> None:
    factory = WfsProviderFactory()

    with pytest.raises(InvalidWfsProviderException) as exception_info:
        factory(AssetType("asset_type_name", "tests.test_wfs.InvalidWfsProvider", {}))

    assert (
        str(exception_info.value)
        == "InvalidWfsProvider.__init__() missing 2 required positional arguments: 'arg1' and 'arg2'"
    )


def test_wfs_provider_factory_raises_when_class_does_not_extend_base() -> None:
    factory = WfsProviderFactory()

    with pytest.raises(InvalidWfsProviderException) as exception_info:
        factory(AssetType("asset_type_name", "tests.test_wfs.InvalidWfsProvider", {"arg1": 1, "arg2": "2"}))

    assert (
        str(exception_info.value)
        == "Instantiated provider 'tests.test_wfs.InvalidWfsProvider' must be an instance of 'BaseWfsProvider'"
    )


def test_wfs_provider_factory_can_produce_provider() -> None:
    factory = WfsProviderFactory()

    provider = factory(AssetType("asset_type_name", "tests.test_wfs.ValidWfsProvider", {}))

    assert isinstance(provider, BaseWfsProvider)
