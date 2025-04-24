from collections.abc import Sequence
from enum import StrEnum
from typing import AsyncIterator, Generic, TypeVar

from plugfs import filesystem
from plugfs.filesystem import Filesystem

from meldingen_core.exceptions import NotFoundException
from meldingen_core.factories import BaseAttachmentFactory
from meldingen_core.image import BaseIngestor
from meldingen_core.models import Attachment, Melding
from meldingen_core.repositories import BaseAttachmentRepository
from meldingen_core.token import TokenVerifier
from meldingen_core.validators import BaseMediaTypeIntegrityValidator, BaseMediaTypeValidator

A = TypeVar("A", bound=Attachment)
M = TypeVar("M", bound=Melding)


class UploadAttachmentAction(Generic[A, M]):
    _create_attachment: BaseAttachmentFactory[A, M]
    _attachment_repository: BaseAttachmentRepository[A]
    _filesystem: Filesystem
    _verify_token: TokenVerifier[M]
    _base_directory: str
    _validate_media_type: BaseMediaTypeValidator
    _validate_media_type_integrity: BaseMediaTypeIntegrityValidator
    _ingest: BaseIngestor[A]

    def __init__(
        self,
        attachment_factory: BaseAttachmentFactory[A, M],
        attachment_repository: BaseAttachmentRepository[A],
        token_verifier: TokenVerifier[M],
        media_type_validator: BaseMediaTypeValidator,
        media_type_integrity_validator: BaseMediaTypeIntegrityValidator,
        ingestor: BaseIngestor[A],
    ):
        self._create_attachment = attachment_factory
        self._attachment_repository = attachment_repository
        self._verify_token = token_verifier
        self._validate_media_type = media_type_validator
        self._validate_media_type_integrity = media_type_integrity_validator
        self._ingest = ingestor

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

        attachment = self._create_attachment(original_filename, melding, media_type)

        await self._ingest(attachment, data)

        await self._attachment_repository.save(attachment)

        return attachment


class AttachmentTypes(StrEnum):
    ORIGINAL = "original"
    OPTIMIZED = "optimized"
    THUMBNAIL = "thumbnail"


class DownloadAttachmentAction(Generic[A, M]):
    _verify_token: TokenVerifier[M]
    _attachment_repository: BaseAttachmentRepository[A]
    _filesystem: Filesystem

    def __init__(
        self,
        token_verifier: TokenVerifier[M],
        attachment_repository: BaseAttachmentRepository[A],
        filesystem: Filesystem,
    ):
        self._verify_token = token_verifier
        self._attachment_repository = attachment_repository
        self._filesystem = filesystem

    async def __call__(
        self, melding_id: int, attachment_id: int, token: str, _type: AttachmentTypes
    ) -> tuple[AsyncIterator[bytes], str]:
        melding = await self._verify_token(melding_id, token)

        attachment = await self._attachment_repository.retrieve(attachment_id)
        if attachment is None:
            raise NotFoundException("Attachment not found")

        if attachment.melding != melding:
            raise NotFoundException(f"Melding with id {melding_id} does not have attachment with id {attachment_id}")

        file_path = attachment.file_path
        media_type = attachment.original_media_type
        if _type == AttachmentTypes.OPTIMIZED:
            if attachment.optimized_path is None:
                raise NotFoundException("Optimized file not found")
            if attachment.optimized_media_type is None:
                raise NotFoundException("Optimized media type not found")
            file_path = attachment.optimized_path
            media_type = attachment.optimized_media_type
        elif _type == AttachmentTypes.THUMBNAIL:
            if attachment.thumbnail_path is None:
                raise NotFoundException("Thumbnail file not found")
            if attachment.thumbnail_media_type is None:
                raise NotFoundException("Thumbnail media type not found")
            file_path = attachment.thumbnail_path
            media_type = attachment.thumbnail_media_type

        try:
            file = await self._filesystem.get_file(file_path)
            return await file.get_iterator(), media_type
        except filesystem.NotFoundException as exception:
            raise NotFoundException("File not found") from exception


class ListAttachmentsAction(Generic[A]):
    _attachment_repository: BaseAttachmentRepository[A]

    def __init__(self, attachment_repository: BaseAttachmentRepository[A]):
        self._attachment_repository = attachment_repository

    async def __call__(self, melding_id: int) -> Sequence[A]:
        return await self._attachment_repository.find_by_melding(melding_id)


class MelderListAttachmentsAction(Generic[A, M]):
    _verify_token: TokenVerifier[M]
    _attachment_repository: BaseAttachmentRepository[A]

    def __init__(self, token_verifier: TokenVerifier[M], attachment_repository: BaseAttachmentRepository[A]):
        self._attachment_repository = attachment_repository
        self._verify_token = token_verifier

    async def __call__(self, melding_id: int, token: str) -> Sequence[A]:
        await self._verify_token(melding_id, token)

        return await self._attachment_repository.find_by_melding(melding_id)


class DeleteAttachmentAction(Generic[A, M]):
    _verify_token: TokenVerifier[M]
    _attachment_repository: BaseAttachmentRepository[A]
    _filesystem: Filesystem

    def __init__(
        self,
        token_verifier: TokenVerifier[M],
        attachment_repository: BaseAttachmentRepository[A],
        filesystem: Filesystem,
    ):
        self._verify_token = token_verifier
        self._attachment_repository = attachment_repository
        self._filesystem = filesystem

    async def __call__(self, melding_id: int, attachment_id: int, token: str) -> None:
        melding = await self._verify_token(melding_id, token)

        attachment = await self._attachment_repository.retrieve(attachment_id)
        if attachment is None:
            raise NotFoundException("Attachment not found")

        if attachment.melding != melding:
            raise NotFoundException(f"Melding with id {melding_id} does not have attachment with id {attachment_id}")

        try:
            await self._filesystem.delete(attachment.file_path)
        except filesystem.NotFoundException as exception:
            raise NotFoundException("File not found") from exception

        await self._attachment_repository.delete(attachment_id)
