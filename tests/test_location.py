# from unittest.mock import AsyncMock, Mock
#
# import pytest
#
# from meldingen_core.location import Address, BaseAddressEnricher, BaseAddressResolver
# from meldingen_core.models import Melding
# from meldingen_core.repositories import BaseMeldingRepository
#
#
# @pytest.mark.anyio
# async def test_address_provider() -> None:
#     melding = Melding("My Melding")
#     lat, lon = 52.3791283, 4.900272
#
#     resolve_address = AsyncMock(BaseAddressResolver)
#     resolve_address.return_value = Address(
#         street="Stationsplein", house_number=39, house_number_addition="K", postal_code="1012AB", city="Amsterdam"
#     )
#
#     repository = Mock(BaseMeldingRepository)
#
#     provide_address: BaseAddressEnricher[Melding] = BaseAddressEnricher(resolve_address, repository)
#
#     await provide_address(melding, lat, lon)
#     resolve_address.assert_called_once_with(lat, lon)
#
#
# @pytest.mark.anyio
# async def test_address_provider_without_address() -> None:
#     melding = Melding("Afval op de stoep")
#     lat, lon = 52.3791283, 4.900272
#
#     resolve_address = AsyncMock(BaseAddressResolver)
#     resolve_address.return_value = None
#     repository = Mock(BaseMeldingRepository)
#
#     provide_address: BaseAddressEnricher[Melding] = BaseAddressEnricher(resolve_address, repository)
#
#     await provide_address(melding, lat, lon)
#     resolve_address.assert_called_once_with(lat, lon)
