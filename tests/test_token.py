from datetime import datetime, timedelta

import pytest

from meldingen_core.models import Melding
from meldingen_core.token import InvalidTokenException, TokenExpiredException, TokenVerifier


def test_token_invalid() -> None:
    melding = Melding("text", token="54321")
    verify_token: TokenVerifier[Melding] = TokenVerifier()

    with pytest.raises(InvalidTokenException):
        verify_token(melding, "12345")


def test_token_expired() -> None:
    token = "123456"
    melding = Melding("text", token=token, token_expires=datetime.now() - timedelta(days=1))
    verify_token: TokenVerifier[Melding] = TokenVerifier()

    with pytest.raises(TokenExpiredException):
        verify_token(melding, token)


def test_token_valid() -> None:
    token = "123456"
    melding = Melding("text", token=token, token_expires=datetime.now() + timedelta(days=1))
    verify_token: TokenVerifier[Melding] = TokenVerifier()

    verify_token(melding, token)
