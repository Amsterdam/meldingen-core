from abc import ABCMeta, abstractmethod
from typing import AsyncIterator


class BaseWfsProvider(metaclass=ABCMeta):
    @abstractmethod
    async def __call__(
        self,
        type_names: str,
        count: int = 1000,
        srs_name: str = "urn:ogc:def:crs:EPSG::4326",
        output_format: str = "application/json",
        filter: str | None = None,
    ) -> tuple[AsyncIterator[bytes], str]:
        ...
