from abc import ABCMeta, abstractmethod  # pragma: no cover
from dataclasses import dataclass  # pragma: no cover
from typing import Generic, TypeVar  # pragma: no cover

from meldingen_core.models import Melding  # pragma: no cover
from meldingen_core.repositories import BaseMeldingRepository  # pragma: no cover


@dataclass  # pragma: no cover
class Address:
    city: str
    postal_code: str
    street: str
    house_number: int
    house_number_addition: str | None = None


T = TypeVar("T", bound=Melding)  # pragma: no cover
A = TypeVar("A", bound=Address)  # pragma: no cover


class BaseAddressResolver(Generic[A], metaclass=ABCMeta):  # pragma: no cover
    """Adapter responsible for getting the address data from another source"""

    @abstractmethod
    async def __call__(self, lat: float, lon: float) -> A | None: ...


class BaseAddressEnricher(Generic[T], metaclass=ABCMeta):  # pragma: no cover
    """Takes a coordinate and adds its address data to the melding"""

    _resolve_address: BaseAddressResolver
    _repository: BaseMeldingRepository[T]

    def __init__(self, resolve_address: BaseAddressResolver, repository: BaseMeldingRepository[T]) -> None:
        self._resolve_address = resolve_address
        self._repository = repository

    @abstractmethod
    async def __call__(self, melding: T, lat: float, lon: float) -> None: ...
