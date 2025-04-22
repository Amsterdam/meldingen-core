from typing import AsyncIterator
from unittest.mock import AsyncMock, Mock

import pytest
from plugfs import filesystem
from plugfs.filesystem import File, Filesystem

from meldingen_core.actions.attachment import (
    AttachmentTypes,
    DeleteAttachmentAction,
    DownloadAttachmentAction,
    ListAttachmentsAction,
    MelderListAttachmentsAction,
    UploadAttachmentAction,
)
from meldingen_core.exceptions import NotFoundException
from meldingen_core.factories import BaseAttachmentFactory
from meldingen_core.image import BaseIngestor
from meldingen_core.models import Attachment, Melding
from meldingen_core.repositories import BaseAttachmentRepository
from meldingen_core.token import TokenVerifier
from meldingen_core.validators import BaseMediaTypeIntegrityValidator, BaseMediaTypeValidator


async def _iterator() -> AsyncIterator[bytes]:
    for chunk in [b"Hello ", b"world", b"!"]:
        yield chunk


class TestUploadAttachmentAction:
    @pytest.mark.anyio
    async def test_can_handle_attachment(self) -> None:
        melding = Melding("melding text")
        token_verifier = AsyncMock(TokenVerifier)
        token_verifier.return_value = melding

        attachment_repository = Mock(BaseAttachmentRepository[Attachment])
        attachment_repository.save = AsyncMock()

        action: UploadAttachmentAction[Attachment, Melding] = UploadAttachmentAction(
            Mock(BaseAttachmentFactory),
            attachment_repository,
            token_verifier,
            Mock(BaseMediaTypeValidator),
            Mock(BaseMediaTypeIntegrityValidator),
            AsyncMock(BaseIngestor),
        )

        iterator = _iterator()

        attachment = await action(123, "super_secret_token", "original_filename.ext", "image/png", b"test", iterator)

        attachment_repository.save.assert_awaited_once_with(attachment)


class TestDownloadAttachmentAction:
    @pytest.mark.anyio
    async def test_attachment_not_found(self) -> None:
        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = None

        action: DownloadAttachmentAction[Attachment, Melding] = DownloadAttachmentAction(
            AsyncMock(TokenVerifier),
            attachment_repository,
            Mock(Filesystem),
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(123, 456, "supersecrettoken", AttachmentTypes.ORIGINAL)

        assert str(exception_info.value) == "Attachment not found"

    @pytest.mark.anyio
    async def test_attachment_does_not_belong_to_melding(self) -> None:
        attachment = Attachment(
            original_filename="bla", original_media_type="image/png", melding=Melding(text="some text")
        )

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        action: DownloadAttachmentAction[Attachment, Melding] = DownloadAttachmentAction(
            AsyncMock(TokenVerifier),
            attachment_repository,
            Mock(Filesystem),
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(123, 456, "supersecrettoken", AttachmentTypes.ORIGINAL)

        assert str(exception_info.value) == "Melding with id 123 does not have attachment with id 456"

    @pytest.mark.anyio
    @pytest.mark.parametrize("_type", AttachmentTypes)
    async def test_can_handle_attachment_download(self, _type: AttachmentTypes) -> None:
        melding = Melding(text="text")
        token_verifier = AsyncMock(TokenVerifier)
        token_verifier.return_value = melding

        attachment = Attachment(original_filename="bla", original_media_type="image/png", melding=melding)
        attachment.file_path = "/path/to/file.ext"
        attachment.original_media_type = "image/png"
        attachment.optimized_path = "/path/to/file-optimized.ext"
        attachment.optimized_media_type = "image/webp"
        attachment.thumbnail_path = "/path/to/file-thumbnail.ext"
        attachment.thumbnail_media_type = "image/webp"

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        action: DownloadAttachmentAction[Attachment, Melding] = DownloadAttachmentAction(
            token_verifier,
            attachment_repository,
            Mock(Filesystem),
        )

        await action(123, 456, "supersecrettoken", _type)

    @pytest.mark.anyio
    async def test_optimized_path_none(self) -> None:
        melding = Melding(text="text")
        token_verifier = AsyncMock(TokenVerifier)
        token_verifier.return_value = melding

        attachment = Attachment(original_filename="bla", original_media_type="image/png", melding=melding)
        attachment.file_path = "/path/to/file.ext"

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        action: DownloadAttachmentAction[Attachment, Melding] = DownloadAttachmentAction(
            token_verifier,
            attachment_repository,
            Mock(Filesystem),
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(123, 456, "supersecrettoken", AttachmentTypes.OPTIMIZED)

        assert str(exception_info.value) == "Optimized file not found"

    @pytest.mark.anyio
    async def test_optimized_media_type_none(self) -> None:
        melding = Melding(text="text")
        token_verifier = AsyncMock(TokenVerifier)
        token_verifier.return_value = melding

        attachment = Attachment(original_filename="bla", original_media_type="image/png", melding=melding)
        attachment.file_path = "/path/to/file.ext"
        attachment.optimized_path = "/path/to/file-optimized.ext"

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        action: DownloadAttachmentAction[Attachment, Melding] = DownloadAttachmentAction(
            token_verifier,
            attachment_repository,
            Mock(Filesystem),
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(123, 456, "supersecrettoken", AttachmentTypes.OPTIMIZED)

        assert str(exception_info.value) == "Optimized media type not found"

    @pytest.mark.anyio
    async def test_thumbnail_path_none(self) -> None:
        melding = Melding(text="text")
        token_verifier = AsyncMock(TokenVerifier)
        token_verifier.return_value = melding

        attachment = Attachment(original_filename="bla", original_media_type="image/png", melding=melding)
        attachment.file_path = "/path/to/file.ext"

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        action: DownloadAttachmentAction[Attachment, Melding] = DownloadAttachmentAction(
            token_verifier,
            attachment_repository,
            Mock(Filesystem),
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(123, 456, "supersecrettoken", AttachmentTypes.THUMBNAIL)

        assert str(exception_info.value) == "Thumbnail file not found"

    @pytest.mark.anyio
    async def test_thumbnail_media_type_none(self) -> None:
        melding = Melding(text="text")
        token_verifier = AsyncMock(TokenVerifier)
        token_verifier.return_value = melding

        attachment = Attachment(original_filename="bla", original_media_type="image/png", melding=melding)
        attachment.file_path = "/path/to/file.ext"
        attachment.thumbnail_path = "/path/to/file-thumbnail.ext"

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        action: DownloadAttachmentAction[Attachment, Melding] = DownloadAttachmentAction(
            token_verifier,
            attachment_repository,
            Mock(Filesystem),
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(123, 456, "supersecrettoken", AttachmentTypes.THUMBNAIL)

        assert str(exception_info.value) == "Thumbnail media type not found"

    @pytest.mark.anyio
    async def test_file_not_found(self) -> None:
        melding = Melding(text="text")
        token_verifier = AsyncMock(TokenVerifier)
        token_verifier.return_value = melding

        attachment = Attachment(original_filename="bla", original_media_type="image/png", melding=melding)
        attachment.file_path = "/path/to/file.ext"

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        file = Mock(File)
        file.get_iterator.side_effect = filesystem.NotFoundException

        filesystem_mock = Mock(Filesystem)
        filesystem_mock.get_file.return_value = file

        action: DownloadAttachmentAction[Attachment, Melding] = DownloadAttachmentAction(
            token_verifier,
            attachment_repository,
            filesystem_mock,
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(123, 456, "supersecrettoken", AttachmentTypes.ORIGINAL)

        assert str(exception_info.value) == "File not found"


class TestListAttachmentsAction:
    @pytest.mark.anyio
    async def test_can_list_attachments(self) -> None:
        melding_id = 123
        repo_attachments: list[Attachment] = []
        repository = Mock(BaseAttachmentRepository)
        repository.find_by_melding.return_value = repo_attachments

        action: ListAttachmentsAction[Attachment, Melding] = ListAttachmentsAction(repository)
        attachments = await action(melding_id)

        assert repo_attachments == attachments
        repository.find_by_melding.assert_awaited_once_with(melding_id)

    @pytest.mark.anyio
    async def test_melder_can_list_attachments(self) -> None:
        token = "supersecrettoken"
        melding_id = 123
        repo_attachments: list[Attachment] = []
        token_verifier = AsyncMock(TokenVerifier)
        repository = Mock(BaseAttachmentRepository)
        repository.find_by_melding.return_value = repo_attachments

        action: MelderListAttachmentsAction[Attachment, Melding] = MelderListAttachmentsAction(
            token_verifier, repository
        )
        attachments = await action(melding_id, token)

        assert repo_attachments == attachments
        token_verifier.assert_awaited_once()
        repository.find_by_melding.assert_awaited_once_with(melding_id)


class TestDeleteAttachmentAction:
    @pytest.mark.anyio
    async def test_attachment_not_found(self) -> None:
        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = None

        action: DeleteAttachmentAction[Attachment, Melding] = DeleteAttachmentAction(
            AsyncMock(TokenVerifier),
            attachment_repository,
            Mock(Filesystem),
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(123, 456, "supersecrettoken")

        assert str(exception_info.value) == "Attachment not found"

    @pytest.mark.anyio
    async def test_attachment_does_not_belong_to_melding(self) -> None:
        attachment = Attachment(
            original_filename="bla", original_media_type="image/png", melding=Melding(text="some text")
        )

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        action: DeleteAttachmentAction[Attachment, Melding] = DeleteAttachmentAction(
            AsyncMock(TokenVerifier),
            attachment_repository,
            Mock(Filesystem),
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(123, 456, "supersecrettoken")

        assert str(exception_info.value) == "Melding with id 123 does not have attachment with id 456"

    @pytest.mark.anyio
    async def test_file_not_found(self) -> None:
        melding = Melding(text="text")
        token_verifier = AsyncMock(TokenVerifier)
        token_verifier.return_value = melding

        attachment = Attachment(original_filename="bla", original_media_type="image/png", melding=melding)
        attachment.file_path = "/path/to/file.ext"

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        filesystem_mock = Mock(Filesystem)
        filesystem_mock.delete.side_effect = filesystem.NotFoundException

        action: DeleteAttachmentAction[Attachment, Melding] = DeleteAttachmentAction(
            token_verifier,
            attachment_repository,
            filesystem_mock,
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(123, 456, "supersecrettoken")

        assert str(exception_info.value) == "File not found"

    @pytest.mark.anyio
    async def test_delete_attachment(self) -> None:
        melding = Melding(text="text")
        token_verifier = AsyncMock(TokenVerifier)
        token_verifier.return_value = melding

        attachment = Attachment(original_filename="bla", original_media_type="image/png", melding=melding)
        attachment.file_path = "/path/to/file.ext"

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        filesystem_mock = Mock(Filesystem)

        action: DeleteAttachmentAction[Attachment, Melding] = DeleteAttachmentAction(
            token_verifier,
            attachment_repository,
            filesystem_mock,
        )

        await action(123, 456, "supersecrettoken")

        filesystem_mock.delete.assert_awaited_once_with(attachment.file_path)
        attachment_repository.delete.assert_awaited_once_with(456)
