from typing import TypeVar
from abc import ABCMeta, abstractmethod
from meldingen_core.models import Melding

T = TypeVar("T", bound=Melding)

class MeldingLocationIngestor(metaclass=ABCMeta):

    @abstractmethod
    async def __call__(self, melding: Melding, geojson: dict) -> Melding: ...
