from meldingen_core.actions.base import (
    BaseCreateAction,
    BaseDeleteAction,
    BaseListAction,
    BaseRetrieveAction,
    BaseUpdateAction,
)
from meldingen_core.models import User


class UserCreateAction[T: User](BaseCreateAction[T]):
    """Action that add a user."""


class UserUpdateAction[T: User](BaseUpdateAction[T]):
    """Action that updates a user."""


class UserListAction[T: User](BaseListAction[T]):
    """Action that retrieves a list of users."""


class UserRetrieveAction[T: User](BaseRetrieveAction[T]):
    """Action that retrieves a user."""


class UserDeleteAction[T: User](BaseDeleteAction[T]):
    """Action that deletes a user."""
