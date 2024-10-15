from typing import AsyncIterator
from unittest.mock import AsyncMock, Mock

import pytest
from plugfs import filesystem
from plugfs.filesystem import File, Filesystem

from meldingen_core.actions.attachment import DownloadAttachmentAction, UploadAttachmentAction
from meldingen_core.exceptions import NotFoundException
from meldingen_core.factories import BaseAttachmentFactory
from meldingen_core.models import Attachment, Melding
from meldingen_core.repositories import BaseAttachmentRepository, BaseMeldingRepository
from meldingen_core.token import TokenVerifier
from meldingen_core.validators import BaseMediaTypeIntegrityValidator, BaseMediaTypeValidator


async def _iterator() -> AsyncIterator[bytes]:
    for chunk in [b"Hello ", b"world", b"!"]:
        yield chunk


class TestUploadAttachmentAction:
    @pytest.mark.anyio
    async def test_melding_not_found(self) -> None:
        melding_repository = Mock(BaseMeldingRepository)
        melding_repository.retrieve.return_value = None

        action: UploadAttachmentAction[Attachment, Melding, Melding] = UploadAttachmentAction(
            Mock(BaseAttachmentFactory),
            Mock(BaseAttachmentRepository),
            melding_repository,
            Mock(Filesystem),
            Mock(TokenVerifier),
            Mock(BaseMediaTypeValidator),
            Mock(BaseMediaTypeIntegrityValidator),
            "/tmp",
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(123, "super_secret_token", "original_filename.ext", "image/png", _iterator())

        assert str(exception_info.value) == "Melding not found"

    @pytest.mark.anyio
    async def test_can_handle_attachment(self) -> None:
        melding = Melding("melding text")

        melding_repository = Mock(BaseMeldingRepository)
        melding_repository.retrieve.return_value = melding

        filesystem = Mock(Filesystem)

        attachment_repository = Mock(BaseAttachmentRepository)

        action: UploadAttachmentAction[Attachment, Melding, Melding] = UploadAttachmentAction(
            Mock(BaseAttachmentFactory),
            attachment_repository,
            melding_repository,
            filesystem,
            Mock(TokenVerifier),
            Mock(BaseMediaTypeValidator),
            AsyncMock(BaseMediaTypeIntegrityValidator),
            "/tmp",
        )

        iterator = _iterator()

        attachment = await action(123, "super_secret_token", "original_filename.ext", "image/png", iterator)

        filesystem.makedirs.assert_awaited_once()
        filesystem.write_iterator.assert_awaited_once_with(attachment.file_path, iterator)
        attachment_repository.save.assert_awaited_once_with(attachment)


class TestDownloadAttachmentAction:
    @pytest.mark.anyio
    async def test_melding_not_found(self) -> None:
        melding_repository = Mock(BaseMeldingRepository)
        melding_repository.retrieve.return_value = None

        action: DownloadAttachmentAction[Melding, Melding] = DownloadAttachmentAction(
            melding_repository,
            Mock(TokenVerifier),
            Mock(BaseAttachmentRepository),
            Mock(Filesystem),
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(123, 456, "supersecrettoken")

        assert str(exception_info.value) == "Melding not found"

    @pytest.mark.anyio
    async def test_attachment_not_found(self) -> None:
        melding_repository = Mock(BaseMeldingRepository)
        melding_repository.retrieve.return_value = Melding(text="text")

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = None

        action: DownloadAttachmentAction[Melding, Melding] = DownloadAttachmentAction(
            melding_repository,
            Mock(TokenVerifier),
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

        melding_repository = Mock(BaseMeldingRepository)
        melding_repository.retrieve.return_value = melding

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        action: DownloadAttachmentAction[Melding, Melding] = DownloadAttachmentAction(
            melding_repository,
            Mock(TokenVerifier),
            attachment_repository,
            Mock(Filesystem),
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(123, 456, "supersecrettoken")

        assert str(exception_info.value) == "Melding with id 123 does not have attachment with id 456"

    @pytest.mark.anyio
    async def test_can_handle_attachment_download(self) -> None:
        melding = Melding(text="text")
        attachment = Attachment("bla", melding)
        attachment.file_path = "/path/to/file.ext"

        melding_repository = Mock(BaseMeldingRepository)
        melding_repository.retrieve.return_value = melding

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        action: DownloadAttachmentAction[Melding, Melding] = DownloadAttachmentAction(
            melding_repository,
            Mock(TokenVerifier),
            attachment_repository,
            Mock(Filesystem),
        )

        await action(123, 456, "supersecrettoken")

    @pytest.mark.anyio
    async def test_file_not_found(self) -> None:
        melding = Melding(text="text")
        attachment = Attachment("bla", melding)
        attachment.file_path = "/path/to/file.ext"

        melding_repository = Mock(BaseMeldingRepository)
        melding_repository.retrieve.return_value = melding

        attachment_repository = Mock(BaseAttachmentRepository)
        attachment_repository.retrieve.return_value = attachment

        file = Mock(File)
        file.get_iterator.side_effect = filesystem.NotFoundException

        filesystem_mock = Mock(Filesystem)
        filesystem_mock.get_file.return_value = file

        action: DownloadAttachmentAction[Melding, Melding] = DownloadAttachmentAction(
            melding_repository,
            Mock(TokenVerifier),
            attachment_repository,
            filesystem_mock,
        )

        with pytest.raises(NotFoundException) as exception_info:
            await action(123, 456, "supersecrettoken")

        assert str(exception_info.value) == "File not found"
