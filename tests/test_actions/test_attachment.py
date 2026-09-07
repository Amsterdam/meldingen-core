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
    MelderDeleteAttachmentAction,
    UploadAttachmentAction,
)
from meldingen_core.exceptions import NotFoundException
from meldingen_core.factories import BaseAttachmentFactory
from meldingen_core.image import BaseIngestor
from meldingen_core.models import Attachment, Melding, User
from meldingen_core.repositories import BaseAttachmentRepository, BaseMeldingRepository
from meldingen_core.repository_item import RepositoryItem
from meldingen_core.validators import (
    AttachmentLimitReachedException,
    BaseAttachmentLimitValidator,
    BaseMediaTypeIntegrityValidator,
    BaseMediaTypeValidator,
)


async def _iterator() -> AsyncIterator[bytes]:
    for chunk in [b"Hello ", b"world", b"!"]:
        yield chunk


class TestDownloadAttachmentAction:
    @pytest.mark.anyio
    async def test_attachment_not_found(self) -> None:
        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = None

        action: DownloadAttachmentAction[Attachment, Melding] = DownloadAttachmentAction(
            AsyncMock(RepositoryItem),
            attachment_repository,
            Mock(Filesystem),
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(123, 456, AttachmentTypes.ORIGINAL)

        assert str(exception_info.value) == "Attachment not found"

    @pytest.mark.anyio
    async def test_attachment_does_not_belong_to_melding(self) -> None:
        attachment = Attachment(
            id=1, original_filename="bla", original_media_type="image/png", melding=Melding(text="some text")
        )

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        action: DownloadAttachmentAction[Attachment, Melding] = DownloadAttachmentAction(
            AsyncMock(RepositoryItem),
            attachment_repository,
            Mock(Filesystem),
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(123, 456, AttachmentTypes.ORIGINAL)

        assert str(exception_info.value) == "Melding with id 123 does not have attachment with id 456"

    @pytest.mark.anyio
    @pytest.mark.parametrize("_type", AttachmentTypes)
    async def test_can_handle_attachment_download(self, _type: AttachmentTypes) -> None:
        melding = Melding(text="text")
        repository_item_retrieve = AsyncMock(RepositoryItem)
        repository_item_retrieve.return_value = melding

        attachment = Attachment(id=1, original_filename="bla", original_media_type="image/png", melding=melding)
        attachment.file_path = "/path/to/file.ext"
        attachment.original_media_type = "image/png"
        attachment.optimized_path = "/path/to/file-optimized.ext"
        attachment.optimized_media_type = "image/webp"
        attachment.thumbnail_path = "/path/to/file-thumbnail.ext"
        attachment.thumbnail_media_type = "image/webp"

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        action: DownloadAttachmentAction[Attachment, Melding] = DownloadAttachmentAction(
            repository_item_retrieve,
            attachment_repository,
            Mock(Filesystem),
        )

        await action(123, 456, _type)

    @pytest.mark.anyio
    async def test_optimized_path_none(self) -> None:
        melding = Melding(text="text")
        repository_item_retrieve = AsyncMock(RepositoryItem)
        repository_item_retrieve.return_value = melding

        attachment = Attachment(id=1, original_filename="bla", original_media_type="image/png", melding=melding)
        attachment.file_path = "/path/to/file.ext"

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        action: DownloadAttachmentAction[Attachment, Melding] = DownloadAttachmentAction(
            repository_item_retrieve,
            attachment_repository,
            Mock(Filesystem),
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(123, 456, AttachmentTypes.OPTIMIZED)

        assert str(exception_info.value) == "Optimized file not found"

    @pytest.mark.anyio
    async def test_optimized_media_type_none(self) -> None:
        melding = Melding(text="text")
        repository_item_retrieve = AsyncMock(RepositoryItem)
        repository_item_retrieve.return_value = melding

        attachment = Attachment(id=1, original_filename="bla", original_media_type="image/png", melding=melding)
        attachment.file_path = "/path/to/file.ext"
        attachment.optimized_path = "/path/to/file-optimized.ext"

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        action: DownloadAttachmentAction[Attachment, Melding] = DownloadAttachmentAction(
            repository_item_retrieve,
            attachment_repository,
            Mock(Filesystem),
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(123, 456, AttachmentTypes.OPTIMIZED)

        assert str(exception_info.value) == "Optimized media type not found"

    @pytest.mark.anyio
    async def test_thumbnail_path_none(self) -> None:
        melding = Melding(text="text")
        repository_item_retrieve = AsyncMock(RepositoryItem)
        repository_item_retrieve.return_value = melding

        attachment = Attachment(id=1, original_filename="bla", original_media_type="image/png", melding=melding)
        attachment.file_path = "/path/to/file.ext"

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        action: DownloadAttachmentAction[Attachment, Melding] = DownloadAttachmentAction(
            repository_item_retrieve,
            attachment_repository,
            Mock(Filesystem),
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(123, 456, AttachmentTypes.THUMBNAIL)

        assert str(exception_info.value) == "Thumbnail file not found"

    @pytest.mark.anyio
    async def test_thumbnail_media_type_none(self) -> None:
        melding = Melding(text="text")
        repository_item_retrieve = AsyncMock(RepositoryItem)
        repository_item_retrieve.return_value = melding

        attachment = Attachment(id=1, original_filename="bla", original_media_type="image/png", melding=melding)
        attachment.file_path = "/path/to/file.ext"
        attachment.thumbnail_path = "/path/to/file-thumbnail.ext"

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        action: DownloadAttachmentAction[Attachment, Melding] = DownloadAttachmentAction(
            repository_item_retrieve,
            attachment_repository,
            Mock(Filesystem),
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(123, 456, AttachmentTypes.THUMBNAIL)

        assert str(exception_info.value) == "Thumbnail media type not found"

    @pytest.mark.anyio
    async def test_file_not_found(self) -> None:
        melding = Melding(text="text")
        repository_item_retrieve = AsyncMock(RepositoryItem)
        repository_item_retrieve.return_value = melding

        attachment = Attachment(id=1, original_filename="bla", original_media_type="image/png", melding=melding)
        attachment.file_path = "/path/to/file.ext"

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        file = Mock(File)
        file.get_iterator.side_effect = filesystem.NotFoundException

        filesystem_mock = Mock(Filesystem)
        filesystem_mock.get_file.return_value = file

        action: DownloadAttachmentAction[Attachment, Melding] = DownloadAttachmentAction(
            repository_item_retrieve,
            attachment_repository,
            filesystem_mock,
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(123, 456, AttachmentTypes.ORIGINAL)

        assert str(exception_info.value) == "File not found"


class TestListAttachmentsAction:
    @pytest.mark.anyio
    async def test_can_list_attachments(self) -> None:
        melding_id = 123
        repo_attachments: list[Attachment] = []
        repository = Mock(BaseAttachmentRepository)
        repository.find_by_melding.return_value = repo_attachments

        action: ListAttachmentsAction[Attachment] = ListAttachmentsAction(repository)
        attachments = await action(melding_id)

        assert repo_attachments == attachments
        repository.find_by_melding.assert_awaited_once_with(melding_id)


class TestMelderDeleteAttachmentAction:
    @pytest.mark.anyio
    async def test_attachment_not_found(self) -> None:
        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = None

        action: MelderDeleteAttachmentAction[Attachment, Melding] = MelderDeleteAttachmentAction(
            AsyncMock(RepositoryItem),
            attachment_repository,
            Mock(Filesystem),
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(123, 456)

        assert str(exception_info.value) == "Attachment not found"

    @pytest.mark.anyio
    async def test_attachment_does_not_belong_to_melding(self) -> None:
        attachment = Attachment(
            id=1, original_filename="bla", original_media_type="image/png", melding=Melding(text="some text")
        )

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        action: MelderDeleteAttachmentAction[Attachment, Melding] = MelderDeleteAttachmentAction(
            AsyncMock(RepositoryItem),
            attachment_repository,
            Mock(Filesystem),
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(123, 456)

        assert str(exception_info.value) == "Melding with id 123 does not have attachment with id 456"

    @pytest.mark.anyio
    async def test_file_not_found(self) -> None:
        melding = Melding(text="text")
        repository_item_retrieve = AsyncMock(RepositoryItem)
        repository_item_retrieve.return_value = melding

        attachment = Attachment(id=1, original_filename="bla", original_media_type="image/png", melding=melding)
        attachment.file_path = "/path/to/file.ext"

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        filesystem_mock = Mock(Filesystem)
        filesystem_mock.delete.side_effect = filesystem.NotFoundException

        action: MelderDeleteAttachmentAction[Attachment, Melding] = MelderDeleteAttachmentAction(
            repository_item_retrieve,
            attachment_repository,
            filesystem_mock,
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(123, 456)

        assert str(exception_info.value) == "File not found"

    @pytest.mark.anyio
    async def test_delete_attachment(self) -> None:
        melding = Melding(text="text")
        repository_item_retrieve = AsyncMock(RepositoryItem)
        repository_item_retrieve.return_value = melding

        attachment = Attachment(id=1, original_filename="bla", original_media_type="image/png", melding=melding)
        attachment.file_path = "/path/to/file.ext"

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        filesystem_mock = Mock(Filesystem)

        action: MelderDeleteAttachmentAction[Attachment, Melding] = MelderDeleteAttachmentAction(
            repository_item_retrieve,
            attachment_repository,
            filesystem_mock,
        )

        await action(123, 456)

        filesystem_mock.delete.assert_awaited_once_with(attachment.file_path)
        attachment_repository.delete.assert_awaited_once_with(attachment.id)


class TestDeleteAttachmentAction:
    @pytest.mark.anyio
    async def test_attachment_not_found(self) -> None:
        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = None

        action: DeleteAttachmentAction[Attachment] = DeleteAttachmentAction(
            attachment_repository,
            Mock(Filesystem),
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(456)

        assert str(exception_info.value) == "Attachment not found"

    @pytest.mark.anyio
    async def test_file_not_found(self) -> None:
        attachment = Attachment(
            id=1, original_filename="bla", original_media_type="image/png", melding=Melding(text="text")
        )
        attachment.file_path = "/path/to/file.ext"

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        filesystem_mock = Mock(Filesystem)
        filesystem_mock.delete.side_effect = filesystem.NotFoundException

        action: DeleteAttachmentAction[Attachment] = DeleteAttachmentAction(
            attachment_repository,
            filesystem_mock,
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(456)

        assert str(exception_info.value) == "File not found"

        attachment_repository.delete.assert_not_awaited()

    @pytest.mark.anyio
    async def test_delete_attachment(self) -> None:
        attachment = Attachment(
            id=1, original_filename="bla", original_media_type="image/png", melding=Melding(text="text")
        )
        attachment.file_path = "/path/to/file.ext"

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        filesystem_mock = Mock(Filesystem)

        action: DeleteAttachmentAction[Attachment] = DeleteAttachmentAction(
            attachment_repository,
            filesystem_mock,
        )

        await action(456)

        attachment_repository.retrieve.assert_awaited_once_with(456)
        filesystem_mock.delete.assert_awaited_once_with(attachment.file_path)
        attachment_repository.delete.assert_awaited_once_with(attachment.id)


class TestUploadAttachmentAction:
    @pytest.mark.anyio
    async def test_can_handle_attachment(self) -> None:
        melding_id = 123
        melding = Melding(text="melding text")

        user = User(id=1, username="behandelaar", email="user@example.com")

        attachment_repository = Mock(BaseAttachmentRepository[Attachment])
        attachment_repository.save = AsyncMock()

        melding_repository = AsyncMock(BaseMeldingRepository)
        melding_repository.retrieve.return_value = melding

        action: UploadAttachmentAction[Attachment, Melding, User] = UploadAttachmentAction(
            Mock(BaseAttachmentFactory),
            attachment_repository,
            Mock(BaseMediaTypeValidator),
            Mock(BaseMediaTypeIntegrityValidator),
            AsyncMock(BaseAttachmentLimitValidator),
            AsyncMock(BaseIngestor),
            melding_repository,
        )

        iterator = _iterator()

        attachment = await action(melding_id, "original_filename.ext", "image/png", b"test", iterator, user)

        melding_repository.retrieve.assert_awaited_once_with(melding_id)
        attachment_repository.save.assert_awaited_once_with(attachment)

    @pytest.mark.anyio
    async def test_raises_when_attachment_limit_is_reached(self) -> None:
        melding_id = 123
        melding = Melding(text="melding text")

        user = User(id=1, username="behandelaar", email="user@example.com")

        attachment_repository = Mock(BaseAttachmentRepository[Attachment])
        attachment_repository.save = AsyncMock()

        melding_repository = Mock(BaseMeldingRepository)
        melding_repository.retrieve = AsyncMock(return_value=melding)

        attachment_limit_validator = AsyncMock(BaseAttachmentLimitValidator[Melding])
        attachment_limit_validator.side_effect = AttachmentLimitReachedException()
        ingestor = AsyncMock(BaseIngestor)

        action: UploadAttachmentAction[Attachment, Melding, User] = UploadAttachmentAction(
            Mock(BaseAttachmentFactory),
            attachment_repository,
            Mock(BaseMediaTypeValidator),
            Mock(BaseMediaTypeIntegrityValidator),
            attachment_limit_validator,
            ingestor,
            melding_repository,
        )

        iterator = _iterator()

        with pytest.raises(AttachmentLimitReachedException):
            await action(melding_id, "original_filename.ext", "image/png", b"test", iterator, user)

        melding_repository.retrieve.assert_awaited_once_with(melding_id)
        attachment_limit_validator.assert_awaited_once_with(melding)
        ingestor.assert_not_awaited()
        attachment_repository.save.assert_not_awaited()

    @pytest.mark.anyio
    async def test_raises_when_melding_not_found(self) -> None:
        melding_id = 123

        user = User(id=1, username="behandelaar", email="user@example.com")

        attachment_repository = Mock(BaseAttachmentRepository[Attachment])
        attachment_repository.save = AsyncMock()

        melding_repository = AsyncMock(BaseMeldingRepository)
        melding_repository.retrieve.return_value = None

        action: UploadAttachmentAction[Attachment, Melding, User] = UploadAttachmentAction(
            Mock(BaseAttachmentFactory),
            attachment_repository,
            Mock(BaseMediaTypeValidator),
            Mock(BaseMediaTypeIntegrityValidator),
            AsyncMock(BaseAttachmentLimitValidator[Melding]),
            AsyncMock(BaseIngestor),
            melding_repository,
        )

        iterator = _iterator()

        with pytest.raises(NotFoundException):
            await action(melding_id, "original_filename.ext", "image/png", b"test", iterator, user)

        melding_repository.retrieve.assert_awaited_once_with(melding_id)
        attachment_repository.save.assert_not_awaited()
