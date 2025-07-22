from unittest.mock import AsyncMock, Mock

import pytest

from meldingen_core.classification import BaseClassifierAdapter, ClassificationNotFoundException, Classifier
from meldingen_core.exceptions import NotFoundException
from meldingen_core.models import Classification
from meldingen_core.repositories import BaseClassificationRepository


@pytest.mark.anyio
async def test_classifier() -> None:
    adapter = AsyncMock(BaseClassifierAdapter, return_value="classification_name")
    repository = Mock(BaseClassificationRepository)
    repository.find_by_name = AsyncMock(return_value=Classification(name="classification_name"))

    classify: Classifier[Classification] = Classifier(adapter, repository)

    classification = await classify("text")

    assert classification.name == "classification_name"
    adapter.assert_called_once_with("text")
    repository.find_by_name.assert_called_once_with("classification_name")


@pytest.mark.anyio
async def test_classifier_classification_not_found() -> None:
    adapter = AsyncMock(BaseClassifierAdapter, return_value="classification_name")
    repository = Mock(BaseClassificationRepository)
    repository.find_by_name = AsyncMock(side_effect=NotFoundException())
    classify: Classifier[Classification] = Classifier(adapter, repository)

    with pytest.raises(ClassificationNotFoundException):
        await classify("text")
