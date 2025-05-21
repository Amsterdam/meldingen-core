from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from meldingen_core.models import Melding
from meldingen_core.repositories import BaseMeldingRepository


@dataclass
class AddressSchema:
    street: str | None = None
    house_number: int | None = None
    house_number_addition: str | None = None
    postal_code: str | None = None
    city: str | None = None


M = TypeVar("M", bound=Melding)
A = TypeVar("A", bound=AddressSchema)


class InvalidAPIRequestException(Exception): ...


class BaseAddressResolver(metaclass=ABCMeta):

    @abstractmethod
    async def __call__(self, lon: float, lat: float) -> A: ...


class BaseAddressProviderTask(Generic[M], metaclass=ABCMeta):
    _resolve_address: BaseAddressResolver
    _repository: BaseMeldingRepository[M]

    def __init__(self, address_resolver: BaseAddressResolver, repository: BaseMeldingRepository[M]):
        self._resolve_address = address_resolver
        self._repository = repository

    async def __call__(self, melding: M, lat: float, lon: float) -> None:
        address: AddressSchema = await self._resolve_address(lat, lon)

        if address is None:
            return

        melding.street = address.street
        melding.house_number = address.house_number
        melding.house_number_addition = address.house_number_addition
        melding.postal_code = address.postal_code
        melding.city = address.city

        await self._repository.save(melding)
