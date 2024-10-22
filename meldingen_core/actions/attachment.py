from typing import AsyncIterator, Generic, TypeVar
from uuid import uuid4

from plugfs import filesystem
from plugfs.filesystem import Filesystem

from meldingen_core.exceptions import NotFoundException
from meldingen_core.factories import BaseAttachmentFactory
from meldingen_core.models import Attachment, Melding
from meldingen_core.repositories import BaseAttachmentRepository
from meldingen_core.token import TokenVerifier
from meldingen_core.validators import BaseMediaTypeIntegrityValidator, BaseMediaTypeValidator

A = TypeVar("A", bound=Attachment)
M = TypeVar("M", bound=Melding)
M_co = TypeVar("M_co", bound=Melding, covariant=True)


class UploadAttachmentAction(Generic[A, M, M_co]):
    _create_attachment: BaseAttachmentFactory[A, M]
    _attachment_repository: BaseAttachmentRepository
    _filesystem: Filesystem
    _verify_token: TokenVerifier[M, M_co]
    _base_directory: str
    _validate_media_type: BaseMediaTypeValidator
    _validate_media_type_integrity: BaseMediaTypeIntegrityValidator

    def __init__(
        self,
        attachment_factory: BaseAttachmentFactory[A, M],
        attachment_repository: BaseAttachmentRepository,
        filesystem: Filesystem,
        token_verifier: TokenVerifier[M, M_co],
        media_type_validator: BaseMediaTypeValidator,
        media_type_integrity_validator: BaseMediaTypeIntegrityValidator,
        base_directory: str,
    ):
        self._create_attachment = attachment_factory
        self._attachment_repository = attachment_repository
        self._filesystem = filesystem
        self._verify_token = token_verifier
        self._validate_media_type = media_type_validator
        self._validate_media_type_integrity = media_type_integrity_validator
        self._base_directory = base_directory

    async def __call__(
        self,
        melding_id: int,
        token: str,
        original_filename: str,
        media_type: str,
        data_header: bytes,
        data: AsyncIterator[bytes],
    ) -> A:
        melding = await self._verify_token(melding_id, token)

        self._validate_media_type(media_type)
        self._validate_media_type_integrity(media_type, data_header)

        attachment = self._create_attachment(original_filename, melding)
        path = f"{self._base_directory}/{str(uuid4()).replace("-", "/")}/"
        attachment.file_path = path + original_filename

        await self._filesystem.makedirs(path)
        await self._filesystem.write_iterator(attachment.file_path, data)

        await self._attachment_repository.save(attachment)

        return attachment


class DownloadAttachmentAction(Generic[M, M_co]):
    _verify_token: TokenVerifier[M, M_co]
    _attachment_repository: BaseAttachmentRepository
    _filesystem: Filesystem

    def __init__(
        self,
        token_verifier: TokenVerifier[M, M_co],
        attachment_repository: BaseAttachmentRepository,
        filesystem: Filesystem,
    ):
        self._verify_token = token_verifier
        self._attachment_repository = attachment_repository
        self._filesystem = filesystem

    async def __call__(self, melding_id: int, attachment_id: int, token: str) -> AsyncIterator[bytes]:
        melding = await self._verify_token(melding_id, token)

        attachment = await self._attachment_repository.retrieve(attachment_id)
        if attachment is None:
            raise NotFoundException("Attachment not found")

        if attachment.melding != melding:
            raise NotFoundException(f"Melding with id {melding_id} does not have attachment with id {attachment_id}")

        try:
            file = await self._filesystem.get_file(attachment.file_path)
            return await file.get_iterator()
        except filesystem.NotFoundException as exception:
            raise NotFoundException("File not found") from exception
