from typing import AsyncIterator, Literal

import pytest

from meldingen_core.models import AssetType, AssetTypeArguments
from meldingen_core.wfs import BaseWfsProvider, BaseWfsProviderFactory, InvalidWfsProviderException, WfsProviderFactory


class InvalidWfsProvider:
    def __init__(self, base_url: str) -> None: ...


class ValidWfsProvider(BaseWfsProvider):
    def __init__(self, base_url: str) -> None: ...

    async def __call__(  # type: ignore
        self,
        type_names: str,
        count: int = 1000,
        srs_name: str = "urn:ogc:def:crs:EPSG::4326",
        output_format: Literal["application/json"] = "application/json",
        service: Literal["WFS"] = "WFS",
        version: str = "2.0.0",
        request: Literal["GetFeature"] = "GetFeature",
        filter: str | None = None,
    ) -> tuple[AsyncIterator[bytes], str]: ...


class ValidWfsProviderFactory(BaseWfsProviderFactory):
    def __call__(self) -> BaseWfsProvider:
        if "base_url" not in self._arguments:
            raise ValueError("Missing 'base_url' in arguments")

        return ValidWfsProvider(self._arguments["base_url"])


class InvalidWfsProviderFactory(BaseWfsProviderFactory):
    def __call__(self) -> InvalidWfsProvider:
        if "base_url" not in self._arguments:
            raise ValueError("Missing 'base_url' in arguments")

        return InvalidWfsProvider(self._arguments["base_url"])


class EmptyProviderFactory:
    _arguments: AssetTypeArguments

    def __init__(self, arguments: AssetTypeArguments) -> None:
        self._arguments = arguments


def test_wfs_provider_factory_raises_when_class_name_invalid() -> None:
    factory = WfsProviderFactory()

    with pytest.raises(InvalidWfsProviderException) as exception_info:
        factory(AssetType("asset_type_name", "invalid_value", {}, 3))

    assert str(exception_info.value) == "class_name 'invalid_value' does not contain full path to class"


def test_wfs_provider_factory_raises_when_module_name_invalid() -> None:
    factory = WfsProviderFactory()

    with pytest.raises(InvalidWfsProviderException) as exception_info:
        factory(AssetType("asset_type_name", "invalid_module_name.Test", {}, 3))

    assert str(exception_info.value) == "Failed to find module 'invalid_module_name'"


def test_wfs_provider_factory_raises_when_class_does_not_exist() -> None:
    factory = WfsProviderFactory()

    with pytest.raises(InvalidWfsProviderException) as exception_info:
        factory(AssetType("asset_type_name", "tests.test_wfs.Test", {}, 3))

    assert str(exception_info.value) == "Failed to find class 'Test' in module 'tests.test_wfs'"


def test_wfs_provider_factory_raises_when_arguments_are_invalid() -> None:
    factory = WfsProviderFactory()

    with pytest.raises(ValueError) as exception_info:
        factory(AssetType("asset_type_name", "tests.test_wfs.ValidWfsProviderFactory", {}, 3))

    assert str(exception_info.value) == "Missing 'base_url' in arguments"


def test_wfs_provider_factory_raises_when_class_does_not_extend_base() -> None:
    factory = WfsProviderFactory()

    with pytest.raises(InvalidWfsProviderException) as exception_info:
        factory(
            AssetType(
                "asset_type_name", "tests.test_wfs.EmptyProviderFactory", {"base_url": "www.thisisabaseurl.com"}, 3
            )
        )

    assert str(exception_info.value) == "Invalid provider factory"


def test_wfs_provider_factory_raises_when_class_does_not_produce_base() -> None:
    factory = WfsProviderFactory()

    with pytest.raises(InvalidWfsProviderException) as exception_info:
        factory(
            AssetType(
                "asset_type_name", "tests.test_wfs.InvalidWfsProviderFactory", {"base_url": "www.thisisabaseurl.com"}, 3
            )
        )

    assert (
        str(exception_info.value)
        == "Instantiated provider factory 'tests.test_wfs.InvalidWfsProviderFactory' must produce an instance of 'BaseWfsProvider'"
    )


def test_wfs_provider_factory_can_produce_provider_from_factory() -> None:
    factory = WfsProviderFactory()

    provider = factory(
        AssetType(
            "asset_type_name", "tests.test_wfs.ValidWfsProviderFactory", {"base_url": "www.thisisabaseurl.com"}, 3
        )
    )

    assert isinstance(provider, ValidWfsProvider)
