from typing import TypeVar

from meldingen_core.actions.base import BaseListAction
from meldingen_core.models import Source

T = TypeVar("T", bound=Source)


class SourceListAction(BaseListAction[T]):
    """Action that retrieves a list of sources."""
