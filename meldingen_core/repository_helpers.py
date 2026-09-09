from meldingen_core.exceptions import NotFoundException
from meldingen_core.repositories import BaseRepository


# Helper function to retrieve an item from the repository or raise NotFoundException if not found.
# This function abstracts the common pattern of retrieving an item by its primary key and handling the case where it does not exist.
async def retrieve_or_raise_not_found[T](repository: BaseRepository[T], pk: int, error_message: str | None = None) -> T:
    item = await repository.retrieve(pk)
    if item is None:
        default_error_message = type(repository).__name__ + " item not found"
        raise NotFoundException(error_message or default_error_message)

    return item
