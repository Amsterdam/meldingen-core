from typing import TypeVar

from meldingen_core.actions.base import (
    BaseCreateAction,
    BaseDeleteAction,
    BaseListAction,
    BaseRetrieveAction,
    BaseUpdateAction,
)
from meldingen_core.models import User

T = TypeVar("T", bound=User)


class UserCreateAction(BaseCreateAction[T]):
    """Action that add a user."""


class UserUpdateAction(BaseUpdateAction[T]):
    """Action that updates a user."""


class UserListAction(BaseListAction[T]):
    """Action that retrieves a list of users."""


class UserRetrieveAction(BaseRetrieveAction[T]):
    """Action that retrieves a user."""


class UserDeleteAction(BaseDeleteAction[T]):
    """Action that deletes a user."""
