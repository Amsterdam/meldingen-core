import pytest

from meldingen_core.actions.user import UserCreateAction, UserListAction, UserRetrieveAction, UserDeleteAction
from meldingen_core.models import User
from meldingen_core.repositories import BaseUserRepository

# Fixtures


@pytest.fixture
def unpopulated_users_repository() -> BaseUserRepository:
    class TestUserRepository(BaseUserRepository):
        data: list[User]

        def __init__(self) -> None:
            self.data = []

        def add(self, user: User) -> None:
            self.data.append(user)

        def list(self, *, limit: int | None = None, offset: int | None = None) -> list[User]:
            if limit and offset:
                return self.data[offset : offset + limit]
            elif limit and not offset:
                return self.data[:limit]
            elif not limit and offset:
                return self.data[offset:]
            else:
                return self.data

        def retrieve(self, pk: int) -> User | None:
            for _user in self.data:
                if _user.username == str(pk):
                    return _user
            return None

        def find_by_email(self, email: str) -> User | None:
            for _user in self.data:
                if _user.email == email:
                    return _user
            return None

        def delete(self, pk: int) -> None:
            for _user in self.data[:]:
                if _user.username == str(pk):
                    self.data.remove(_user)
            return None

    repository = TestUserRepository()
    return repository


@pytest.fixture
def populated_users_repository(
    unpopulated_users_repository: BaseUserRepository,
) -> BaseUserRepository:
    for _pk in range(10):
        user = User()
        user.username = f"{_pk}"
        user.email = f"user-{_pk}@example.com"
        unpopulated_users_repository.add(user)

    return unpopulated_users_repository


@pytest.fixture
def users_create_action(
    unpopulated_users_repository: BaseUserRepository,
) -> UserCreateAction:
    return UserCreateAction(unpopulated_users_repository)


@pytest.fixture
def users_list_action(
    populated_users_repository: BaseUserRepository,
) -> UserListAction:
    return UserListAction(populated_users_repository)


@pytest.fixture
def users_retrieve_action(
    populated_users_repository: BaseUserRepository,
) -> UserRetrieveAction:
    return UserRetrieveAction(populated_users_repository)


@pytest.fixture
def users_delete_action(
    populated_users_repository: BaseUserRepository,
) -> UserDeleteAction:
    return UserDeleteAction(populated_users_repository)


# PyTest Classes


class TestUserCreateAction:
    def test_add(self, users_create_action: UserCreateAction) -> None:
        assert len(users_create_action.repository.list()) == 0

        user = User()
        user.username = "1"

        users_create_action(user)

        assert len(users_create_action.repository.list()) == 1
        assert users_create_action.repository.retrieve(pk=1) == user


class TestUserListAction:
    def test_list_all(self, users_list_action: UserListAction) -> None:
        users = users_list_action()

        assert len(users) == 10

    @pytest.mark.parametrize(
        "limit, expected_result",
        [(1, 1), (5, 5), (10, 10), (20, 10)],
    )
    def test_list_limit(self, users_list_action: UserListAction, limit: int, expected_result: int) -> None:
        users = users_list_action(limit=limit)

        assert len(users) == expected_result

    @pytest.mark.parametrize("offset, expected_result", [(1, 9), (5, 5), (10, 0), (20, 0)])
    def test_list_offset(
        self,
        users_list_action: UserListAction,
        offset: int,
        expected_result: int,
    ) -> None:
        users = users_list_action(offset=offset)

        assert len(users) == expected_result

    @pytest.mark.parametrize(
        "limit, offset, expected_result",
        [(10, 0, 10), (5, 0, 5), (10, 10, 0), (20, 0, 10)],
    )
    def test_list_limit_offset(
        self,
        users_list_action: UserListAction,
        limit: int,
        offset: int,
        expected_result: int,
    ) -> None:
        users = users_list_action(limit=limit, offset=offset)

        assert len(users) == expected_result

class TestUserRetrieveAction:
    @pytest.mark.parametrize("pk", [1, 2, 3, 4, 5])
    def test_retrieve_existing_users(self, users_retrieve_action: UserRetrieveAction, pk: int) -> None:
        user = users_retrieve_action(pk=pk)

        assert user is not None
        assert user.username == str(pk)

    @pytest.mark.parametrize("pk", [101, 102, 103, 104, 105])
    def test_retrieve_non_existing_users(self, users_retrieve_action: UserRetrieveAction, pk: int) -> None:
        user = users_retrieve_action(pk=pk)

        assert user is None

class TestUserDeleteAction:
    @pytest.mark.parametrize("pk", [1, 2, 3, 4, 5])
    def test_delete_existing_user(self, users_delete_action: UserDeleteAction, pk: int) -> None:
        assert users_delete_action.repository.retrieve(pk=pk) is not None
        assert len(users_delete_action.repository.list()) == 10

        users_delete_action(pk=pk)

        assert users_delete_action.repository.retrieve(pk=pk) is None
        assert len(users_delete_action.repository.list()) == 9

    @pytest.mark.parametrize("pk", [101, 102, 103, 104, 105])
    def test_delete_non_existing_user(self, users_delete_action: UserDeleteAction, pk: int) -> None:
        assert users_delete_action.repository.retrieve(pk=pk) is None
        assert len(users_delete_action.repository.list()) == 10

        users_delete_action(pk=pk)

        assert len(users_delete_action.repository.list()) == 10
