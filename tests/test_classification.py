from unittest.mock import Mock, AsyncMock

import pytest

from meldingen_core.classification import Classifier, BaseClassifierAdapter
from meldingen_core.models import Classification
from meldingen_core.repositories import BaseClassificationRepository


@pytest.mark.asyncio
async def test_classifier() -> None:
    adapter = AsyncMock(BaseClassifierAdapter, return_value="classification_name")
    repository = Mock(BaseClassificationRepository)
    repository.find_by_name = AsyncMock(return_value=Classification(name="classification_name"))

    classify = Classifier(adapter, repository)

    classification = await classify("text")

    assert classification.name == "classification_name"
    adapter.assert_called_once_with("text")
    repository.find_by_name.assert_called_once_with("classification_name")
