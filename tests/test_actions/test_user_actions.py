from collections.abc import Collection

import pytest
from pytest_mock import MockerFixture

from meldingen_core.actions.user import (
    UserCreateAction,
    UserDeleteAction,
    UserListAction,
    UserRetrieveAction,
    UserUpdateAction,
)
from meldingen_core.models import User
from meldingen_core.repositories import BaseUserRepository

# Fixtures


@pytest.fixture
def mocked_repository() -> BaseUserRepository:
    class MockMeldingRepository(BaseUserRepository):
        async def save(self, obj: User) -> None:
            return None

        async def list(self, *, limit: int | None = None, offset: int | None = None) -> Collection[User]:
            return []

        async def retrieve(self, pk: int) -> User | None:
            return None

        async def delete(self, pk: int) -> None:
            return None

    mocked_repository = MockMeldingRepository()
    return mocked_repository


@pytest.fixture
def users_create_action(
    mocked_repository: BaseUserRepository,
) -> UserCreateAction:
    return UserCreateAction(mocked_repository)


@pytest.fixture
def users_update_action(
    mocked_repository: BaseUserRepository,
) -> UserUpdateAction:
    return UserUpdateAction(mocked_repository)


@pytest.fixture
def users_list_action(
    mocked_repository: BaseUserRepository,
) -> UserListAction:
    return UserListAction(mocked_repository)


@pytest.fixture
def users_retrieve_action(
    mocked_repository: BaseUserRepository,
) -> UserRetrieveAction:
    return UserRetrieveAction(mocked_repository)


@pytest.fixture
def users_delete_action(
    mocked_repository: BaseUserRepository,
) -> UserDeleteAction:
    return UserDeleteAction(mocked_repository)


# PyTest Classes


class TestUserCreateAction:
    @pytest.mark.asyncio
    async def test_add(self, users_create_action: UserCreateAction, mocker: MockerFixture) -> None:
        spy = mocker.spy(users_create_action._repository, "save")

        user = User()
        user.username = "1"

        await users_create_action(user)

        spy.assert_called_once_with(user)


class TestUserListAction:
    @pytest.mark.asyncio
    async def test_list_all(self, users_list_action: UserListAction, mocker: MockerFixture) -> None:
        spy = mocker.spy(users_list_action._repository, "list")

        await users_list_action()

        spy.assert_called_once()

    @pytest.mark.parametrize(
        "limit",
        [1, 5, 10, 20],
    )
    @pytest.mark.asyncio
    async def test_list_limit(self, users_list_action: UserListAction, limit: int, mocker: MockerFixture) -> None:
        spy = mocker.spy(users_list_action._repository, "list")

        await users_list_action(limit=limit)

        spy.assert_called_once_with(limit=limit, offset=None)

    @pytest.mark.parametrize("offset", [1, 5, 10, 20])
    @pytest.mark.asyncio
    async def test_list_offset(
        self,
        users_list_action: UserListAction,
        offset: int,
        mocker: MockerFixture,
    ) -> None:
        spy = mocker.spy(users_list_action._repository, "list")

        await users_list_action(offset=offset)

        spy.assert_called_once_with(limit=None, offset=offset)

    @pytest.mark.parametrize(
        "limit, offset",
        [(10, 0), (5, 0), (10, 10), (20, 0)],
    )
    @pytest.mark.asyncio
    async def test_list_limit_offset(
        self,
        users_list_action: UserListAction,
        limit: int,
        offset: int,
        mocker: MockerFixture,
    ) -> None:
        spy = mocker.spy(users_list_action._repository, "list")

        await users_list_action(limit=limit, offset=offset)

        spy.assert_called_once_with(limit=limit, offset=offset)


class TestUserRetrieveAction:
    @pytest.mark.parametrize("pk", [1, 2, 3, 4, 5])
    @pytest.mark.asyncio
    async def test_retrieve_user(
        self, users_retrieve_action: UserRetrieveAction, pk: int, mocker: MockerFixture
    ) -> None:
        spy = mocker.spy(users_retrieve_action._repository, "retrieve")

        await users_retrieve_action(pk=pk)

        spy.assert_called_once_with(pk=pk)


class TestUserDeleteAction:
    @pytest.mark.parametrize("pk", [1, 2, 3, 4, 5])
    @pytest.mark.asyncio
    async def test_delete_user(self, users_delete_action: UserDeleteAction, pk: int, mocker: MockerFixture) -> None:
        spy = mocker.spy(users_delete_action._repository, "delete")

        await users_delete_action(pk=pk)

        spy.assert_called_once_with(pk=pk)


class TestUserUpdateAction:
    @pytest.mark.parametrize(
        "pk, username, email",
        [
            (1, "user1", "user1@example.com"),
            (1, "user1", "other-user-1@example.com"),
            (1, "other-user-1", "user1@example.com"),
            (1, "other-user-1", "other-user-1@example.com"),
        ],
    )
    @pytest.mark.asyncio
    async def test_update_user(
        self, users_update_action: UserUpdateAction, pk: int, username: str, email: str, mocker: MockerFixture
    ) -> None:
        spy = mocker.spy(users_update_action._repository, "save")

        user = User()
        user.username = "1"

        await users_update_action(user)

        spy.assert_called_once_with(user)
