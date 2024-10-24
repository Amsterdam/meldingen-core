from typing import AsyncIterator
from unittest.mock import AsyncMock, Mock

import pytest
from plugfs import filesystem
from plugfs.filesystem import File, Filesystem

from meldingen_core.actions.attachment import DownloadAttachmentAction, ListAttachmentsAction, UploadAttachmentAction
from meldingen_core.exceptions import NotFoundException
from meldingen_core.factories import BaseAttachmentFactory
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

        filesystem = Mock(Filesystem)

        attachment_repository = Mock(BaseAttachmentRepository[Attachment, Attachment])

        action: UploadAttachmentAction[Attachment, Attachment, Melding, Melding] = UploadAttachmentAction(
            Mock(BaseAttachmentFactory),
            attachment_repository,
            filesystem,
            token_verifier,
            Mock(BaseMediaTypeValidator),
            Mock(BaseMediaTypeIntegrityValidator),
            "/tmp",
        )

        iterator = _iterator()

        attachment = await action(123, "super_secret_token", "original_filename.ext", "image/png", b"test", iterator)

        filesystem.makedirs.assert_awaited_once()
        filesystem.write_iterator.assert_awaited_once_with(attachment.file_path, iterator)
        attachment_repository.save.assert_awaited_once_with(attachment)


class TestDownloadAttachmentAction:
    @pytest.mark.anyio
    async def test_attachment_not_found(self) -> None:
        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = None

        action: DownloadAttachmentAction[Attachment, Attachment, Melding, Melding] = DownloadAttachmentAction(
            AsyncMock(TokenVerifier),
            attachment_repository,
            Mock(Filesystem),
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(123, 456, "supersecrettoken")

        assert str(exception_info.value) == "Attachment not found"

    @pytest.mark.anyio
    async def test_attachment_does_not_belong_to_melding(self) -> None:
        melding = Melding(text="text")
        attachment = Attachment("bla", Melding(text="some text"))

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        action: DownloadAttachmentAction[Attachment, Attachment, Melding, Melding] = DownloadAttachmentAction(
            AsyncMock(TokenVerifier),
            attachment_repository,
            Mock(Filesystem),
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(123, 456, "supersecrettoken")

        assert str(exception_info.value) == "Melding with id 123 does not have attachment with id 456"

    @pytest.mark.anyio
    async def test_can_handle_attachment_download(self) -> None:
        melding = Melding(text="text")
        token_verifier = AsyncMock(TokenVerifier)
        token_verifier.return_value = melding

        attachment = Attachment("bla", melding)
        attachment.file_path = "/path/to/file.ext"

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        action: DownloadAttachmentAction[Attachment, Attachment, Melding, Melding] = DownloadAttachmentAction(
            token_verifier,
            attachment_repository,
            Mock(Filesystem),
        )

        await action(123, 456, "supersecrettoken")

    @pytest.mark.anyio
    async def test_file_not_found(self) -> None:
        melding = Melding(text="text")
        token_verifier = AsyncMock(TokenVerifier)
        token_verifier.return_value = melding

        attachment = Attachment("bla", melding)
        attachment.file_path = "/path/to/file.ext"

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        file = Mock(File)
        file.get_iterator.side_effect = filesystem.NotFoundException

        filesystem_mock = Mock(Filesystem)
        filesystem_mock.get_file.return_value = file

        action: DownloadAttachmentAction[Attachment, Attachment, Melding, Melding] = DownloadAttachmentAction(
            token_verifier,
            attachment_repository,
            filesystem_mock,
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(123, 456, "supersecrettoken")

        assert str(exception_info.value) == "File not found"


class TestListAttachmentsAction:
    @pytest.mark.anyio
    async def test_can_list_attachments(self) -> None:
        token = "supersecrettoken"
        melding_id = 123
        repo_attachments: list[Attachment] = []
        token_verifier = AsyncMock(TokenVerifier)
        repository = Mock(BaseAttachmentRepository)
        repository.find_by_melding.return_value = repo_attachments

        action: ListAttachmentsAction[Attachment, Attachment, Melding, Melding] = ListAttachmentsAction(
            token_verifier, repository
        )
        attachments = await action(melding_id, token)

        assert repo_attachments == attachments
        token_verifier.assert_awaited_once()
        repository.find_by_melding.assert_awaited_once_with(melding_id)
