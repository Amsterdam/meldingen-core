from plugfs.filesystem import Filesystem

from meldingen_core.exceptions import NotFoundException
from meldingen_core.models import Attachment
from meldingen_core.repositories import BaseMeldingRepository, BaseAttachmentRepository


class UploadAttachmentAction:
    _attachment_repository: BaseAttachmentRepository
    _melding_repository: BaseMeldingRepository
    _filesystem: Filesystem

    async def __call__(self, melding_id: int, original_filename: str, data: bytes) -> Attachment:
        melding = await self._melding_repository.retrieve(melding_id)
        if melding is None:
            raise NotFoundException('Melding not found')

        attachment = Attachment(original_filename, melding)
        attachment.file_path = attachment.unique_identifier.replace("-", "/") + "/" + original_filename

        await self._filesystem.write(attachment.file_path, data)

        await self._attachment_repository.save(attachment)

        return attachment
