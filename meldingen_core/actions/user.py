from meldingen_core.models import User
from meldingen_core.repositories import BaseUserRepository


class UserCreateAction:
    """Action that stores a user."""

    repository: BaseUserRepository

    def __init__(self, repository: BaseUserRepository):
        self.repository = repository

    def __call__(self, user: User) -> None:
        self.repository.add(user)


class UserListAction:
    """Action that retrieves a list of users."""

    repository: BaseUserRepository

    def __init__(self, repository: BaseUserRepository):
        self.repository = repository

    def __call__(self, *, limit: int | None = None, offset: int | None = None) -> list[User]:
        return self.repository.list(limit=limit, offset=offset)


class UserRetrieveAction:
    """Action that retrieves a user."""

    repository: BaseUserRepository

    def __init__(self, repository: BaseUserRepository):
        self.repository = repository

    def __call__(self, pk: int) -> User | None:
        return self.repository.retrieve(pk=pk)
