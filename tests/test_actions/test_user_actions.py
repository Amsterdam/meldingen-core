from unittest.mock import Mock

from meldingen_core.actions.user import (
    UserCreateAction,
    UserDeleteAction,
    UserListAction,
    UserRetrieveAction,
    UserUpdateAction,
)
from meldingen_core.models import User
from meldingen_core.repositories import BaseUserRepository


def test_can_instantiate_user_create_action() -> None:
    action: UserCreateAction[User] = UserCreateAction(Mock(BaseUserRepository))
    assert isinstance(action, UserCreateAction)


def test_can_instantiate_user_list_action() -> None:
    action: UserListAction[User] = UserListAction(Mock(BaseUserRepository))
    assert isinstance(action, UserListAction)


def test_can_instantiate_user_retrieve_action() -> None:
    action: UserRetrieveAction[User] = UserRetrieveAction(Mock(BaseUserRepository))
    assert isinstance(action, UserRetrieveAction)


def test_can_instantiate_user_update_action() -> None:
    action: UserUpdateAction[User] = UserUpdateAction(Mock(BaseUserRepository))
    assert isinstance(action, UserUpdateAction)


def test_can_instantiate_user_delete_action() -> None:
    action: UserDeleteAction[User] = UserDeleteAction(Mock(BaseUserRepository))
    assert isinstance(action, UserDeleteAction)
