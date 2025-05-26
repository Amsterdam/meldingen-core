from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from meldingen_core.models import Melding
from meldingen_core.repositories import BaseMeldingRepository


@dataclass
class Address:
    city: str
    postal_code: str
    street: str
    house_number: int
    house_number_addition: str | None = None


M = TypeVar("M", bound=Melding)
A = TypeVar("A", bound=Address)


class BaseAddressResolver(metaclass=ABCMeta):
    """Adapter responsible for getting the address data from another source"""

    @abstractmethod
    async def __call__(self, lon: float, lat: float) -> A: ...


class BaseAddressEnricher(Generic[M], metaclass=ABCMeta):
    """Takes a coordinate and adds its address data to the melding"""

    _resolve_address: BaseAddressResolver
    _repository: BaseMeldingRepository[M]

    def __init__(self, resolve_address: BaseAddressResolver, repository: BaseMeldingRepository) -> None:
        self._resolve_address = resolve_address
        self._repository = repository

    @abstractmethod
    async def __call__(self, melding: M, lat: float, lon: float) -> None: ...
