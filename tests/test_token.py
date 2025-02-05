from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from meldingen_core.exceptions import NotFoundException
from meldingen_core.models import Melding
from meldingen_core.repositories import BaseMeldingRepository
from meldingen_core.token import InvalidTokenException, TokenExpiredException, TokenVerifier


@pytest.mark.anyio
async def test_melding_not_found() -> None:
    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = None

    verify_token: TokenVerifier[Melding] = TokenVerifier(repository)
    with pytest.raises(NotFoundException):
        await verify_token(123, "")


@pytest.mark.anyio
async def test_token_invalid() -> None:
    melding = Melding("text", token="54321")

    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = melding

    verify_token: TokenVerifier[Melding] = TokenVerifier(repository)

    with pytest.raises(InvalidTokenException):
        await verify_token(123, "12345")


@pytest.mark.anyio
async def test_token_expired() -> None:
    token = "123456"
    melding = Melding("text", token=token, token_expires=datetime.now() - timedelta(days=1))
    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = melding

    verify_token: TokenVerifier[Melding] = TokenVerifier(repository)

    with pytest.raises(TokenExpiredException):
        await verify_token(123, token)


@pytest.mark.anyio
async def test_token_valid() -> None:
    token = "123456"
    repo_melding = Melding("text", token=token, token_expires=datetime.now() + timedelta(days=1))

    repository = Mock(BaseMeldingRepository)
    repository.retrieve.return_value = repo_melding

    verify_token: TokenVerifier[Melding] = TokenVerifier(repository)

    melding = await verify_token(123, token)
    assert melding == repo_melding
