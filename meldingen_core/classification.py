import enum
import logging
from abc import ABCMeta, abstractmethod

from meldingen_core.exceptions import NotFoundException
from meldingen_core.models import Classification
from meldingen_core.repositories import BaseClassificationRepository

log = logging.getLogger(__name__)


class ClassificationNotFoundException(NotFoundException): ...


class ClassifierErrorCodes(enum.Enum):
    CLASSIFIER_ADAPTER_FAILED = "CLASSIFIER_ADAPTER_FAILED"
    CLASSIFIER_ADAPTER_RETURNED_NONE = "CLASSIFIER_ADAPTER_RETURNED_NONE"
    CLASSIFIER_CLASSIFICATION_NOT_FOUND = "CLASSIFIER_CLASSIFICATION_NOT_FOUND"


class BaseClassifierAdapter(metaclass=ABCMeta):
    name: str

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def __call__(self, text: str) -> str | None:
        """Accepts a text as input and returns the classification name."""


class Classifier[C: Classification]:
    _adapters: list[BaseClassifierAdapter]
    _repository: BaseClassificationRepository[C]

    def __init__(
        self,
        adapters: list[BaseClassifierAdapter],
        repository: BaseClassificationRepository[C],
        classification_default_name: str,
    ):
        self._adapters = adapters
        self._repository = repository
        self._classification_default_name = classification_default_name

    async def __call__(self, text: str) -> tuple[C, str | None]:
        classifier_result = None
        classification = None

        for adapter in self._adapters:
            try:
                classifier_result = await adapter(text)
                if classifier_result is not None:
                    # Adapters found a classification, break the loop. Use the first result found.
                    break
                else:
                    log.error(
                        "%s: Classification adapter: '%s' returned None",
                        ClassifierErrorCodes.CLASSIFIER_ADAPTER_RETURNED_NONE.value,
                        adapter.name,
                    )
            except Exception as e:  # noqa: BLE001
                log.error(
                    "%s: Classification adapter: '%s' failed with error '%s'.",
                    ClassifierErrorCodes.CLASSIFIER_ADAPTER_FAILED.value,
                    adapter.name,
                    str(e),
                )

        if classifier_result is None:
            log.error(
                "%s: Classification adapter(s) did not return a valid classification, using fallback '%s'",
                ClassifierErrorCodes.CLASSIFIER_ADAPTER_RETURNED_NONE.value,
                self._classification_default_name,
            )
        else:
            try:
                classification = await self._repository.find_by_name(classifier_result)
            except NotFoundException:
                log.error(
                    "%s: Classification with classification name '%s' does not exist, using fallback '%s'",
                    ClassifierErrorCodes.CLASSIFIER_CLASSIFICATION_NOT_FOUND.value,
                    classifier_result,
                    self._classification_default_name,
                )

        if not classification:
            classification = await self._repository.find_by_name(self._classification_default_name)

        return classification, classifier_result
