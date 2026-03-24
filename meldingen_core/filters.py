from dataclasses import dataclass
from typing import Sequence

from meldingen_core.statemachine import BaseMeldingState


@dataclass
class ListFilters:
    name_contains: str | None = None


@dataclass
class MeldingListFilters:
    area: str | None = None
    states: Sequence[BaseMeldingState] | None = None
