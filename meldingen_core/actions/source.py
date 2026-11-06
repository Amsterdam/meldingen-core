from meldingen_core.actions.base import BaseListAction
from meldingen_core.filters import RepositoryFilters
from meldingen_core.models import Source


class SourceListAction[T: Source, F: RepositoryFilters](BaseListAction[T, F]):
    """Action that retrieves a list of sources."""
