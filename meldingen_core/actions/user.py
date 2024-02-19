from meldingen_core.actions.base import BaseCreateAction, BaseListAction, BaseRetrieveAction, BaseUpdateAction
from meldingen_core.models import User
from meldingen_core.repositories import BaseUserRepository


class UserCreateAction(BaseCreateAction[User, User]):
    """Action that add a user."""


class UserUpdateAction(BaseUpdateAction[User, User]):
    """Action that updates a user."""


class UserListAction(BaseListAction[User, User]):
    """Action that retrieves a list of users."""


class UserRetrieveAction(BaseRetrieveAction[User, User]):
    """Action that retrieves a user."""


class UserDeleteAction:
    """Action that deletes a user."""

    repository: BaseUserRepository

    def __init__(self, repository: BaseUserRepository):
        self.repository = repository

    async def __call__(self, pk: int) -> None:
        await self.repository.delete(pk=pk)
