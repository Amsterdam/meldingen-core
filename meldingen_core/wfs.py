from abc import ABCMeta, abstractmethod
from importlib import import_module
from typing import AsyncIterator

from meldingen_core.models import AssetType


class BaseWfsProvider(metaclass=ABCMeta):
    @abstractmethod
    async def __call__(
        self,
        type_names: str,
        count: int = 1000,
        srs_name: str = "urn:ogc:def:crs:EPSG::4326",
        output_format: str = "application/json",
        filter: str | None = None,
    ) -> tuple[AsyncIterator[bytes], str]: ...


class InvalidWfsProviderException(Exception): ...


class WfsProviderFactory:
    def __call__(self, asset_type: AssetType) -> BaseWfsProvider:
        module_name, class_name = asset_type.class_name.rsplit(".", 1)
        module = import_module(module_name)

        provider = getattr(module, class_name)(**asset_type.arguments)
        if not isinstance(provider, BaseWfsProvider):
            raise InvalidWfsProviderException("Invalid Wfs Provider")

        return provider
