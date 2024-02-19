from collections.abc import Collection

from meldingen_core.actions.base import BaseCreateAction, BaseRetrieveAction
from meldingen_core.models import User
from meldingen_core.repositories import BaseUserRepository


class UserSaveAction:
    """Action that stores a user."""

    repository: BaseUserRepository

    def __init__(self, repository: BaseUserRepository):
        self.repository = repository

    async def __call__(self, user: User) -> None:
        await self.repository.save(user)


class UserCreateAction(BaseCreateAction[User, User]):
    """Action that add a user."""


class UserUpdateAction(UserSaveAction):
    """Action that updates a user."""


class UserListAction:
    """Action that retrieves a list of users."""

    repository: BaseUserRepository

    def __init__(self, repository: BaseUserRepository):
        self.repository = repository

    async def __call__(self, *, limit: int | None = None, offset: int | None = None) -> Collection[User]:
        return await self.repository.list(limit=limit, offset=offset)


class UserRetrieveAction(BaseRetrieveAction[User, User]):
    """Action that retrieves a user."""


class UserDeleteAction:
    """Action that deletes a user."""

    repository: BaseUserRepository

    def __init__(self, repository: BaseUserRepository):
        self.repository = repository

    async def __call__(self, pk: int) -> None:
        await self.repository.delete(pk=pk)
