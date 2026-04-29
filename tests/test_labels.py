from unittest.mock import Mock

from meldingen_core.labels import BaseLabelReplacer
from meldingen_core.models import Label, Melding
from meldingen_core.repositories import BaseLabelRepository


class _LabelReplacerStub(BaseLabelReplacer[Melding, Label]):
    async def __call__(self, melding: Melding, label_ids: list[int]) -> Melding:
        return melding


def test_base_label_replacer_stores_repository() -> None:
    repository = Mock(BaseLabelRepository)

    replacer = _LabelReplacerStub(repository)

    assert replacer._label_repository is repository
