from typing import Generic, TypeVar

from plugfs.filesystem import Filesystem

from meldingen_core.exceptions import NotFoundException
from meldingen_core.models import Attachment, Melding
from meldingen_core.repositories import BaseAttachmentRepository, BaseMeldingRepository

M = TypeVar("M", bound=Melding)
M_co = TypeVar("M_co", bound=Melding, covariant=True)


class UploadAttachmentAction(Generic[M, M_co]):
    _attachment_repository: BaseAttachmentRepository
    _melding_repository: BaseMeldingRepository[M, M_co]
    _filesystem: Filesystem

    def __init__(
        self,
        attachment_repository: BaseAttachmentRepository,
        melding_repository: BaseMeldingRepository[M, M_co],
        filesystem: Filesystem,
    ):
        self._attachment_repository = attachment_repository
        self._melding_repository = melding_repository
        self._filesystem = filesystem

    async def __call__(self, melding_id: int, original_filename: str, data: bytes) -> Attachment:
        melding = await self._melding_repository.retrieve(melding_id)
        if melding is None:
            raise NotFoundException("Melding not found")

        attachment = Attachment(original_filename, melding)
        attachment.file_path = attachment.unique_identifier.replace("-", "/") + "/" + original_filename

        await self._filesystem.write(attachment.file_path, data)

        await self._attachment_repository.save(attachment)

        return attachment
