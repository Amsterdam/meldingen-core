from typing import Generic, TypeVar
from uuid import uuid4

from plugfs.filesystem import Filesystem

from meldingen_core.exceptions import NotFoundException
from meldingen_core.factories import BaseAttachmentFactory
from meldingen_core.models import Attachment, Melding
from meldingen_core.repositories import BaseAttachmentRepository, BaseMeldingRepository
from meldingen_core.token import TokenVerifier

A = TypeVar("A", bound=Attachment)
M = TypeVar("M", bound=Melding)
M_co = TypeVar("M_co", bound=Melding, covariant=True)


class UploadAttachmentAction(Generic[A, M, M_co]):
    _create_attachment: BaseAttachmentFactory[A, M]
    _attachment_repository: BaseAttachmentRepository
    _melding_repository: BaseMeldingRepository[M, M_co]
    _filesystem: Filesystem
    _verify_token: TokenVerifier[M]
    _base_directory: str

    def __init__(
        self,
        attachment_factory: BaseAttachmentFactory[A, M],
        attachment_repository: BaseAttachmentRepository,
        melding_repository: BaseMeldingRepository[M, M_co],
        filesystem: Filesystem,
        token_verifier: TokenVerifier[M],
        base_directory: str,
    ):
        self._create_attachment = attachment_factory
        self._attachment_repository = attachment_repository
        self._melding_repository = melding_repository
        self._filesystem = filesystem
        self._verify_token = token_verifier
        self._base_directory = base_directory

    async def __call__(self, melding_id: int, token: str, original_filename: str, data: bytes) -> A:
        melding = await self._melding_repository.retrieve(melding_id)
        if melding is None:
            raise NotFoundException("Melding not found")

        self._verify_token(melding, token)

        attachment = self._create_attachment(original_filename, melding)
        path = f"{self._base_directory}/{str(uuid4()).replace("-", "/")}/"
        attachment.file_path = path + original_filename

        await self._filesystem.makedirs(path)
        await self._filesystem.write(attachment.file_path, data)

        await self._attachment_repository.save(attachment)

        return attachment
