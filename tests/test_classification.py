import logging
from unittest.mock import AsyncMock, Mock

import pytest
from _pytest.logging import LogCaptureFixture

from meldingen_core.classification import (
    BaseClassifierAdapter,
    Classifier,
)
from meldingen_core.exceptions import NotFoundException
from meldingen_core.models import Classification
from meldingen_core.repositories import BaseClassificationRepository

props = {
    "service_level_objective_day_type": "work_days",
    "service_level_objective_days": 5,
    "service_level_objective_text": "Foo Bar",
}

default_classification = Classification(
    name="default_classification_name",
    **props,
)

valid_classification = Classification(
    name="classification_name",
    **props,
)

classification_fallback_custom = Classification(
    name="classification_fallback_custom_name",
    **props,
)


@pytest.mark.anyio
async def test_classifier() -> None:
    adapter = AsyncMock(BaseClassifierAdapter, name="LLM Model 1", return_value="classification_name")
    repository = Mock(BaseClassificationRepository)
    repository.find_by_name = AsyncMock(return_value=valid_classification)

    classify: Classifier[Classification] = Classifier([adapter], repository, default_classification)

    classification, classifier_adapter_result_initial = await classify("text")

    assert classification.name == "classification_name"
    assert classifier_adapter_result_initial == classification.name
    adapter.assert_called_once_with("text")
    repository.find_by_name.assert_called_once_with("classification_name")


@pytest.mark.anyio
async def test_classifier_adapter_raises_and_returns_default(caplog: LogCaptureFixture) -> None:
    error = Exception("Adapter failed")
    adapter = AsyncMock(BaseClassifierAdapter, side_effect=error)
    adapter.name = "LLM Model 1"

    repository = Mock(BaseClassificationRepository)

    classify: Classifier[Classification] = Classifier([adapter], repository, default_classification)
    with caplog.at_level(logging.ERROR):
        classification, classifier_adapter_result_initial = await classify("text")

    assert classification.name == "default_classification_name"
    assert classifier_adapter_result_initial == None
    assert any(
        record.message == "Classification adapter: 'LLM Model 1' failed: Adapter failed" for record in caplog.records
    )


@pytest.mark.anyio
async def test_classifier_multiple_adapters_raises_and_returns_default(caplog: LogCaptureFixture) -> None:
    error1 = Exception("Adapter 1 failed")
    adapter1 = AsyncMock(BaseClassifierAdapter, side_effect=error1)
    adapter1.name = "LLM Model 1"

    error2 = Exception("Adapter 2 failed")
    adapter2 = AsyncMock(BaseClassifierAdapter, side_effect=error2)
    adapter2.name = "LLM Model 2"

    repository = Mock(BaseClassificationRepository)
    classify: Classifier[Classification] = Classifier([adapter1, adapter2], repository, default_classification)

    with caplog.at_level(logging.ERROR):
        classification, classifier_adapter_result_initial = await classify("text")

    assert classification.name == "default_classification_name"
    assert classifier_adapter_result_initial == None
    messages = [record.message for record in caplog.records]
    assert "Classification adapter: 'LLM Model 1' failed: Adapter 1 failed" in messages
    assert "Classification adapter: 'LLM Model 2' failed: Adapter 2 failed" in messages


@pytest.mark.anyio
async def test_classifier_multiple_adapters_returns_second_classification(caplog: LogCaptureFixture) -> None:
    adapter1 = AsyncMock(BaseClassifierAdapter, return_value=None)
    adapter1.name = "LLM Model 1"

    adapter2 = AsyncMock(BaseClassifierAdapter, return_value="classification_name")
    adapter2.name = "Machine learning model"

    repository = Mock(BaseClassificationRepository)
    repository.find_by_name = AsyncMock(return_value=valid_classification)

    classify: Classifier[Classification] = Classifier([adapter1, adapter2], repository, default_classification)

    with caplog.at_level(logging.INFO):
        classification, classifier_adapter_result_initial = await classify("text")

    assert classification.name == "classification_name"
    assert classifier_adapter_result_initial == "classification_name"
    assert any(record.message == "Classification adapter: 'LLM Model 1' returned None" for record in caplog.records)


@pytest.mark.anyio
async def test_classifier_multiple_adapters_first_fails_then_returns_second_classification(
    caplog: LogCaptureFixture,
) -> None:
    """
    Test that the classifier returns the second classification when the first adapter fails.
    Second adapter is a custom one that just returns a fallback classification that's always available,
    but not the same as the default_classification. Effectively overriding the default classification.
    """
    error1 = Exception("Adapter 1 failed")
    adapter1 = AsyncMock(BaseClassifierAdapter, side_effect=error1)
    adapter1.name = "LLM Model 1"

    class CustomFallbackAdapter(BaseClassifierAdapter):
        async def __call__(self, _text: str) -> str | None:
            return classification_fallback_custom.name

    adapter2 = CustomFallbackAdapter("LLM Model 2")

    repository = Mock(BaseClassificationRepository)
    repository.find_by_name = AsyncMock(return_value=classification_fallback_custom)

    classify: Classifier[Classification] = Classifier([adapter1, adapter2], repository, default_classification)

    with caplog.at_level(logging.ERROR):
        classification, classifier_adapter_result_initial = await classify("text")

    assert classification.name == "classification_fallback_custom_name"
    assert classifier_adapter_result_initial == "classification_fallback_custom_name"
    assert any(
        record.message == "Classification adapter: 'LLM Model 1' failed: Adapter 1 failed" for record in caplog.records
    )


@pytest.mark.anyio
async def test_classifier_classification_not_found(caplog: LogCaptureFixture) -> None:
    adapter = AsyncMock(BaseClassifierAdapter, return_value="classification_name")
    adapter.name = "LLM Model 1"

    repository = Mock(BaseClassificationRepository)
    repository.find_by_name = AsyncMock(side_effect=NotFoundException())
    classify: Classifier[Classification] = Classifier([adapter], repository, default_classification)

    with caplog.at_level(logging.ERROR):
        classification, classifier_adapter_result_initial = await classify("text")

    assert classification.name == "default_classification_name"
    assert classifier_adapter_result_initial == "classification_name"
    assert any(
        record.message == "Classification with classification name 'classification_name' does not exist, "
        "using fallback 'default_classification_name'"
        for record in caplog.records
    )
