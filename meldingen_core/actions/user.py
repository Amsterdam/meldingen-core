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
T_co = TypeVar("T_co", covariant=True, bound=User)


class UserCreateAction(BaseCreateAction[User, User]):
    """Action that add a user."""


class UserUpdateAction(BaseUpdateAction[User, User]):
    """Action that updates a user."""


class UserListAction(BaseListAction[T, T_co]):
    """Action that retrieves a list of users."""


class UserRetrieveAction(BaseRetrieveAction[T, T_co]):
    """Action that retrieves a user."""


class UserDeleteAction(BaseDeleteAction[User, User]):
    """Action that deletes a user."""
