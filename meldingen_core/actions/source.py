from meldingen_core.actions.base import BaseListAction
from meldingen_core.models import Source


class SourceListAction[T: Source](BaseListAction[T]):
    """Action that retrieves a list of sources."""
