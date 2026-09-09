from collections.abc import Sequence
from dataclasses import dataclass

from meldingen_core.statemachine import BaseMeldingState


@dataclass
class NameListFilters:
    name_contains: str | None = None


@dataclass
class MeldingListFilters:
    area: str | None = None
    states: Sequence[BaseMeldingState] | None = None
