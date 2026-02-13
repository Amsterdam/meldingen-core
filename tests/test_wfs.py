from typing import AsyncIterator, Literal, cast

import pytest

from meldingen_core.models import AssetType, AssetTypeArguments
from meldingen_core.wfs import (
    BaseWfsProvider,
    BaseWfsProviderFactory,
    InvalidWfsProviderException,
    WfsProviderFactory,
)


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

    async def validate(self) -> None:
        if "base_url" not in self._arguments:
            raise InvalidWfsProviderException("Missing 'base_url' in arguments")


class InvalidWfsProviderFactory(BaseWfsProviderFactory):
    def __call__(self) -> BaseWfsProvider:
        if "base_url" not in self._arguments:
            raise ValueError("Missing 'base_url' in arguments")

        # We want to test what happens when the returned class does not extend BaseWfsProvider, but mypy complains
        # So we cast it first to suppress the error
        return cast(BaseWfsProvider, InvalidWfsProvider(self._arguments["base_url"]))

    async def validate(self) -> None:
        if "base_url" not in self._arguments:
            raise InvalidWfsProviderException("Missing 'base_url' in arguments")


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


def test_wfs_provider_factory_can_produce_provider_from_factory_with_too_many_arguments() -> None:
    factory = WfsProviderFactory()

    provider = factory(
        AssetType(
            "asset_type_name",
            "tests.test_wfs.ValidWfsProviderFactory",
            {"base_url": "www.thisisabaseurl.com", "extra_argument": "this extra argument is ignored"},
            3,
        )
    )

    assert isinstance(provider, ValidWfsProvider)


@pytest.mark.anyio
async def test_wfs_provider_factory_validate_raises_when_class_name_invalid() -> None:
    factory = WfsProviderFactory()
    with pytest.raises(InvalidWfsProviderException) as exception_info:
        await factory.validate(AssetType("asset_type_name", "invalid_value", {}, 3))
    assert str(exception_info.value) == "class_name 'invalid_value' does not contain full path to class"


@pytest.mark.anyio
async def test_wfs_provider_factory_validate_raises_when_module_name_invalid() -> None:
    factory = WfsProviderFactory()
    with pytest.raises(InvalidWfsProviderException) as exception_info:
        await factory.validate(AssetType("asset_type_name", "invalid_module_name.Test", {}, 3))
    assert str(exception_info.value) == "Failed to find module 'invalid_module_name'"


@pytest.mark.anyio
async def test_wfs_provider_factory_validate_raises_when_class_does_not_exist() -> None:
    factory = WfsProviderFactory()
    with pytest.raises(InvalidWfsProviderException) as exception_info:
        await factory.validate(AssetType("asset_type_name", "tests.test_wfs.Test", {}, 3))
    assert str(exception_info.value) == "Failed to find class 'Test' in module 'tests.test_wfs'"


@pytest.mark.anyio
async def test_wfs_provider_factory_validate_raises_when_class_does_not_extend_base() -> None:
    factory = WfsProviderFactory()
    with pytest.raises(InvalidWfsProviderException) as exception_info:
        await factory.validate(
            AssetType(
                "asset_type_name", "tests.test_wfs.EmptyProviderFactory", {"base_url": "www.thisisabaseurl.com"}, 3
            )
        )
    assert str(exception_info.value) == "Invalid provider factory"


@pytest.mark.anyio
async def test_wfs_provider_factory_validate_raises_when_factory_validate_fails() -> None:
    factory = WfsProviderFactory()
    with pytest.raises(InvalidWfsProviderException):
        await factory.validate(AssetType("asset_type_name", "tests.test_wfs.ValidWfsProviderFactory", {}, 3))


@pytest.mark.anyio
async def test_wfs_provider_factory_validate_succeeds() -> None:
    factory = WfsProviderFactory()
    await factory.validate(
        AssetType(
            "asset_type_name", "tests.test_wfs.ValidWfsProviderFactory", {"base_url": "www.thisisabaseurl.com"}, 3
        )
    )
