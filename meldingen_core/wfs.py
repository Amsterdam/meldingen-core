from abc import ABCMeta, abstractmethod
from importlib import import_module
from typing import AsyncIterator, Literal

from meldingen_core.models import AssetType, AssetTypeArguments


class BaseWfsProvider(metaclass=ABCMeta):
    @abstractmethod
    async def __call__(
        self,
        type_names: str,
        count: int = 1000,
        srs_name: str = "urn:ogc:def:crs:EPSG::4326",
        output_format: Literal["application/json"] = "application/json",
        service: Literal["WFS"] = "WFS",
        version: str = "2.0.0",
        request: Literal["GetFeature"] = "GetFeature",
        filter: str | None = None,
    ) -> AsyncIterator[bytes]: ...


class BaseWfsProviderFactory(metaclass=ABCMeta):
    _arguments: AssetTypeArguments

    @abstractmethod
    def __call__(self) -> BaseWfsProvider: ...

    def __init__(self, arguments: AssetTypeArguments) -> None:
        self._arguments = arguments


class InvalidWfsProviderException(Exception): ...


class WfsProviderFactory:
    def __call__(self, asset_type: AssetType) -> BaseWfsProvider:
        try:
            module_name, class_name = asset_type.class_name.rsplit(".", 1)
        except ValueError as e:
            raise InvalidWfsProviderException(
                f"class_name '{asset_type.class_name}' does not contain full path to class"
            ) from e

        try:
            module = import_module(module_name)
        except ModuleNotFoundError as e:
            raise InvalidWfsProviderException(f"Failed to find module '{module_name}'") from e

        try:
            klass = getattr(module, class_name)
        except AttributeError as e:
            raise InvalidWfsProviderException(f"Failed to find class '{class_name}' in module '{module_name}'") from e

        provider_factory = klass(asset_type.arguments)

        if not isinstance(provider_factory, BaseWfsProviderFactory):
            raise InvalidWfsProviderException("Invalid provider factory")

        provider = provider_factory()

        if not isinstance(provider, BaseWfsProvider):
            raise InvalidWfsProviderException(
                f"Instantiated provider factory '{asset_type.class_name}' must produce an instance of 'BaseWfsProvider'"
            )

        return provider
