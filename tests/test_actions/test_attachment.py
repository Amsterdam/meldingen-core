from unittest.mock import Mock

import pytest
from plugfs.filesystem import Filesystem

from meldingen_core.actions.attachment import UploadAttachmentAction
from meldingen_core.exceptions import NotFoundException
from meldingen_core.factories import BaseAttachmentFactory
from meldingen_core.models import Attachment, Melding
from meldingen_core.repositories import BaseAttachmentRepository, BaseMeldingRepository
from meldingen_core.token import TokenVerifier


@pytest.mark.anyio
async def test_melding_not_found() -> None:
    melding_repository = Mock(BaseMeldingRepository)
    melding_repository.retrieve.return_value = None

    action: UploadAttachmentAction[Attachment, Melding, Melding] = UploadAttachmentAction(
        Mock(BaseAttachmentFactory),
        Mock(BaseAttachmentRepository),
        melding_repository,
        Mock(Filesystem),
        Mock(TokenVerifier),
        "/tmp",
    )

    with pytest.raises(NotFoundException) as exception_info:
        await action(123, "super_secret_token", "original_filename.ext", b"Hello World!")

    assert str(exception_info.value) == "Melding not found"


@pytest.mark.anyio
async def test_can_handle_attachment() -> None:
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
        "/tmp",
    )

    data = b"Hello World!"

    attachment = await action(123, "super_secret_token", "original_filename.ext", data)

    filesystem.makedirs.assert_awaited_once()
    filesystem.write.assert_awaited_once_with(attachment.file_path, data)
    attachment_repository.save.assert_awaited_once_with(attachment)
